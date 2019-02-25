#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#import json
import math
import numpy as np
import h5py
import csv
#import matplotlib.pyplot as plt
#import matplotlib
#import pandas as pd
#import seaborn as sns
#from matplotlib.colors import LinearSegmentedColormap
#matplotlib.style.use('ggplot')
#from pandas import DataFrame
from config import *
#import jsonlines


class TrustMan(object):
	""" input values """
	n_providers=0
	n_intermidiaries=0
	n_fraudsters=0
	l_chain=0
	n_calls=0
	n_calls_fraud=0
	frauds_percentage=0

	""" output values of updateMatrix() """
	disguised_behaviour = 0
	malicious_behaviour = 0

	n_coop_providers = 0
	n_coop_intermidiaries = 0

	frauds_detector_counter = 0 #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
	accusations_counter_ref = 0 #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
	accusations_counter = 0 #conta quante accuse vengono effettivamente fatte a casua della non risposta degli intermediari


	global fraudsters_behaviour
	global Revenue
	global Tscore

	def __init__(self, providers, intermidiaries, fraudsters_percentage, l_chain, calls, frauds_percentage, provider_participation
		, intermidiaries_participation):
		super(TrustMan, self).__init__()

		self.n_providers = int(providers)
		self.n_intermidiaries = int(intermidiaries)

		self.n_fraudsters = int(int(intermidiaries) * int(fraudsters_percentage) // 100)
		self.l_chain=int(l_chain)
		self.n_calls = int(calls)
		self.n_calls_fraud = int(int(calls) * int(frauds_percentage) // 100)
		self.frauds_percentage = frauds_percentage
		self.n_coop_providers = int(int(provider_participation)*int(providers)//100)
		self.n_coop_intermidiaries = int(int(intermidiaries_participation)*(int(intermidiaries)-self.n_fraudsters)//100)

		self.fraudsters_behaviour = [[0 for k in range(2)] for i in range(self.n_fraudsters)]
		self.Revenue = [0 for g in range(self.n_intermidiaries)]
		self.Tscore = [0 for m in range(self.n_intermidiaries)]




	def updateMatrix(self, traces_file):

		N = self.n_providers + self.n_intermidiaries
		POS = 0 #const
		NEG = 1 #const
		
		#M = [[[0 for k in range(2)] for j in range(N)] for i in range(N)]
		with h5py.File("matrix.hdf5", "a") as f:
			f.create_dataset("bigM", shape=(N,N,2), dtype=np.uint8)

		fx = h5py.File('matrix.hdf5', 'a')
		matrix = fx['bigM']

		count=0

		with open(traces_file, 'r') as f:
			reader = csv.reader(f)
			traces = list(reader)

			for trace in traces:

				Tools.printProgress( count, self.n_calls)
				count+=1

				self.measure_fraudsters_behaviour(trace)

				if self.isCoopProvider(int(trace[Csv.TERMIN])) and not self.isFraud(int(trace[Csv.FRAUD])):
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					matrix[origin,nextop,POS]=matrix[origin,nextop,POS] + 1
					for i in range(self.l_chain-1):
						source = int(trace[Csv.TRANSIT+i])
						target = int(trace[Csv.TRANSIT+i+1])
						if self.isCoopIntermidiary(source):
							#M[source][target][POS] = M[source][target][POS] + 1
							matrix[source,target,POS] = matrix[source,target,POS] + 1
							#if TrustConfig.ref:
							#	Ref[source][target] = Ref[source][target] +1

				if self.isCoopProvider(int(trace[Csv.TERMIN])) and self.isFraud(int(trace[Csv.FRAUD])):
					
					self.frauds_detector_counter += 1
					self.accusations_counter_ref += self.l_chain
					self.accusations_counter += 1 #la prima accusa da origin al primo transit esiste indipendentemente dalla risposta dei tranists
					'''Origin accuses the first transit op'''
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					#M[origin][nextop][1] = M[origin][nextop][1] + 1
					matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] + 1
					if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and not self.isFraudster(nextop) and matrix[origin,nextop,NEG]>0: #condizione sul valore positivo serve a evitare di avere valori negativi
						#M[origin][nextop][1] = M[origin][nextop][1] - 1
						matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] - 1

					'''Transit-i accuses transit-i+1'''
					for i in range(self.l_chain-1):
						source = int(trace[(Csv.TRANSIT+i)])
						target = int(trace[(Csv.TRANSIT+i+1)])
						if self.isCoopIntermidiary(source):
							print("CIOooo")
							#M[source][target][1] = M[source][target][1] + 1
							matrix[source,target,NEG] = matrix[source,target,NEG] + 1
							self.Revenue[target-self.n_providers] +=  TrustMan.calcRevenue()
							#if TrustConfig.ref:
							#    Ref[source][target] = Ref[source][target] +1
							if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and not self.isFraudster(target) and matrix[source,target,NEG]>0:  
								#M[source][target][1] = M[source][target][1] -  1.0 / (i+2)
								matrix[source,target,NEG] = matrix[source,target,NEG] -  1.0 / (i+2)
							if TrustConfig.simmetry_strategy and matrix[target,source,NEG]>=1:  
								#M[source][target][1] = M[source][target][1] - 1
								#M[target][source][1] = M[target][source][1] - 1
								matrix[source,target,NEG] = matrix[source,target,NEG] -  1
								matrix[target,source,NEG] = matrix[target,source,NEG] -  1
						self.accusations_counter += 1
		print("Matrix updated.")

		
		transactions = [[0 for k in range(2)] for i in range(self.n_intermidiaries)]
		for j in range(self.n_providers, N): #scorro ogni intermediario j
			_pos = 0
			_neg = 0
			for i in range(N): #scorro tutti gli accusatori i per un intermediario j
				_pos += matrix[i,j,POS]
				_neg += matrix[i,j,NEG]
			transactions[j-self.n_providers][POS] = _pos
			transactions[j-self.n_providers][NEG] = _neg
		
		print("DEBUG: ref"+str(self.accusations_counter_ref))
		print("DEBUG acc :"+str(self.accusations_counter))
		print("DEBUG disg" + str(self.disguised_behaviour))
		print("DEBUG malis" + str(self.malicious_behaviour))

		print(transactions)

		fx.flush()
		fx.close()

	'''
	def getField(self, trace, flag, opt):
		# id, fraud, origin, termin, l_chain , tranist_1, tranist_2..tranist_n, durattionA, duratinB, tariffA, tariffB
		if flag is "id":
			return trace[0]
		if flag is "fraud":
			return trace[1]
		if flag is "origin":
			return trace[2]
		if flag is "termin":
			return trace[3]
		if flag is "chain":
			return trace[4]
		if flag is "transit":
			return trace[5+opt]
	'''

	def isFraudster(self, index):

		ind = int(index)
		low = self.n_providers+self.n_intermidiaries-self.n_fraudsters
		up =  self.n_providers+self.n_intermidiaries

		if ind in range(low,up):
			return True 
		else:
			return False

	def isFraud(self, value):

		val = int(value)

		if val == 1:
			return True
		else:
			return False

	def isCoopProvider(self, index):

		ind = int(index)
		low = int(self.n_providers/2-self.n_coop_providers/2)
		up =  int(self.n_providers/2 + self.n_coop_providers/2)
		
		if ind in range(low,up):
			return True
		else:
			return False

	def isCoopIntermidiary(self, index):

		ind = int(index)
		low = self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)-int(self.n_coop_intermidiaries/2)
		up =  self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)+int(self.n_coop_intermidiaries/2)

		if ind in range(low,up):
			return True
		else:
			return False

	def measure_fraudsters_behaviour(self, trace):
		for transit_th in range(self.l_chain):
			if self.isFraudster(int(trace[Csv.TRANSIT+transit_th])):
				if not self.isFraud(int(trace[Csv.FRAUD])):
					self.disguised_behaviour += 1 #le transazioni buone fatte da un frodatre nel campione
				else:
					self.malicious_behaviour += 1 #le transazioni maligne fatte da un frodatre nel campione


	@staticmethod       
	def calcRevenue():
		r_bypass = TraceConfig.bypass_revenue*TraceConfig.average_call_duration
		#r_bypass = FraudType.bypass_revenue * trace["durationA"]
		r_fas = TraceConfig.fas_duration*TraceConfig.tariff_international 
		r_lrn = TraceConfig.lrn_revenue * TraceConfig.average_call_duration
		r = 0

		if TraceConfig.fas_fraud:
		    r = r_fas
		if TraceConfig.bypass_fraud:
		    r = r_bypass
		if TraceConfig.bypass_fraud and TraceConfig.fas_fraud:
		    r = r_bypass + r_fas
		if TraceConfig.lrn_fraud:
		    r = r_lrn
		return r




		