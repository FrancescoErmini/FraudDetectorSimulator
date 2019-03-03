#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#import json
import math
import numpy as np
import h5py
import csv
import logging

#import matplotlib.pyplot as plt
#import matplotlib
import pandas as pd
from pandas import DataFrame
#import seaborn as sns
#from matplotlib.colors import LinearSegmentedColormap
#matplotlib.style.use('ggplot')
#from pandas import DataFrame
from config import *
#import jsonlines


class TrustMan(object):




	""" input values
	n_providers=0
	n_intermidiaries=0
	n_fraudsters=0
	l_chain=0
	n_calls=0
	n_calls_fraud=0
	frauds_percentage=0

	n_honests = 0
		n_coop_providers = 0
	n_coop_intermidiaries = 0
	"""

	""" output values of updateMatrix() """



	#global fraudsters_behaviour
	#global Revenue
	#global Tscore

	"""
	fraudsters = 0
	suspected_fraudsters = 0
	suspected_falsenegative = 0
	unknown_fraudsters = 0
	falsenegative = 0

	honests = 0
	suspected_honests = 0
	suspected_falsepositive = 0
	falsepositive = 0
	unknown_honests = 0
	"""
	

	def __init__(self, scenario):
		super(TrustMan, self).__init__()

		self.scenario = scenario
		self.disguised_behaviour = 0
		self.malicious_behaviour = 0



		self.frauds_detector_counter = 0 #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
		self.accusations_counter_ref = 0 #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
		self.accusations_counter = 0 #conta quante accuse vengono effettivamente fatte a casua della non risposta degli intermediari

		"""
		self.scenario.n_providers = int(providers)
		self.scenario.n_intermidiaries = int(intermidiaries)

		self.scenario.n_fraudsters = int(int(intermidiaries) * int(fraudsters_percentage) // 100)
		self.scenario.l_chain=int(l_chain)
		self.scenario.n_calls = int(calls)
		self.scenario.n_calls_fraud = int(int(calls) * int(frauds_percentage) // 100)
		self.scenario.frauds_percentage = frauds_percentage
		self.scenario.n_coop_providers = int(int(provider_participation)*int(providers)//100)
		self.scenario.n_coop_intermidiaries = int(int(intermidiaries_participation)*(int(intermidiaries)-self.scenario.n_fraudsters)//100)
		self.scenario.n_honests = self.scenario.n_intermidiaries - self.scenario.n_fraudsters
		"""

		#self.fraudsters_behaviour = [[0 for k in range(2)] for i in range(self.scenario.n_fraudsters)]
		#self.Revenue = [0 for g in range(self.scenario.n_intermidiaries)]
		#self.Tscore = [0 for m in range(self.scenario.n_intermidiaries)]




	def updateMatrix(self, infile, outfile, logfile):

		
		logging.basicConfig(filename=logfile,level=logging.DEBUG)

		N = self.scenario.n_providers + self.scenario.n_intermidiaries
		POS = 0 #const
		NEG = 1 #const
		
		#M = [[[0 for k in range(2)] for j in range(N)] for i in range(N)]
		with h5py.File(outfile, "a") as f:
			f.create_dataset("fback_matrix", shape=(N,N,2))
			f.create_dataset("normal_matrix", shape=(N,N))
			f.create_dataset("opinion_matrix", shape=(N,N,4))

		fx = h5py.File(outfile, 'a')
		matrix = fx['fback_matrix']

		count=0


		'''
		chunks = pd.read_csv(path+'/traces.csv',chunksize=80, sep=',', index_col=False, header=None)
		for chunk in chunks:
			data = chunk.values #convert DataFrame to numpy
			for trace in data:
		'''
		with open(infile, 'r') as src:
			reader = csv.reader(src)
			traces = list(reader)

		for trace in traces:

				Tools.printProgress( count, self.scenario.n_calls)
				count+=1

				#self.measure_fraudsters_behaviour(trace)

				if self.scenario.isCoopProvider(int(trace[Csv.TERMIN])) and not self.scenario.isFraud(int(trace[Csv.FRAUD])):
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					matrix[origin,nextop,POS]=matrix[origin,nextop,POS] + 1
					for i in range(self.scenario.l_chain-1):
						source = int(trace[Csv.TRANSIT+i])
						target = int(trace[Csv.TRANSIT+i+1])
						if self.scenario.isCoopIntermidiary(source):
							#M[source][target][POS] = M[source][target][POS] + 1
							matrix[source,target,POS] = matrix[source,target,POS] + 1
							'''
							if TrustConfig.ref:
								Ref[source][target] = Ref[source][target] +1
							'''
				if self.scenario.isCoopProvider(int(trace[Csv.TERMIN])) and self.scenario.isFraud(int(trace[Csv.FRAUD])):
					
					self.frauds_detector_counter += 1
					self.accusations_counter_ref += self.scenario.l_chain
					self.accusations_counter += 1 #la prima accusa da origin al primo transit esiste indipendentemente dalla risposta dei tranists
					'''Origin accuses the first transit op'''
					origin = int(trace[Csv.ORIGIN])
					nextop = int(trace[Csv.TRANSIT])
					#M[origin][nextop][1] = M[origin][nextop][1] + 1
					matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] + 1
					if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and not self.scenario.isFraudster(nextop) and matrix[origin,nextop,NEG]>0: #condizione sul valore positivo serve a evitare di avere valori negativi
						#M[origin][nextop][1] = M[origin][nextop][1] - 1
						matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] - 1

					'''Transit-i accuses transit-i+1'''
					for i in range(self.scenario.l_chain-1):
						source = int(trace[(Csv.TRANSIT+i)])
						target = int(trace[(Csv.TRANSIT+i+1)])
						if self.scenario.isCoopIntermidiary(source):
							
							#M[source][target][1] = M[source][target][1] + 1
							matrix[source,target,NEG] = matrix[source,target,NEG] + 1
							#self.Revenue[target-self.scenario.n_providers] +=  TrustMan.calcRevenue()
							#if TrustConfig.ref:
							#    Ref[source][target] = Ref[source][target] +1
							if TrustConfig.simmetry_strategy:			
								#M[source][target][1] = M[source][target][1] - 1
								#M[target][source][1] = M[target][source][1] - 1
								if not self.scenario.isFraudster(target):
									matrix[source,target,NEG] = matrix[source,target,NEG] -  1
								if not self.scenario.isFraudster(source) and matrix[target,source,NEG]>=1:
									matrix[target,source,NEG] = matrix[target,source,NEG] -  1
							
							if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and not self.scenario.isFraudster(target) and matrix[source,target,NEG]>=1:  
								#M[source][target][1] = M[source][target][1] -  1.0 / (i+2)
								matrix[source,target,NEG] = matrix[source,target,NEG] -  1.0 / (i+2)
								
						self.accusations_counter += 1
		print("Matrix updated..")

		print("missed accusations: " + str(self.accusations_counter)+"/"+str(self.accusations_counter_ref))
		print("missed frauds: " + str(self.frauds_detector_counter) + str(self.scenario.n_calls_fraud))


		
		print("Log pos neg values")
		
		#logging.debug('This message should go to the log file')
		


		for j in range(self.scenario.n_providers, N): #scorro ogni intermediario j

			op = j - self.scenario.n_providers
			#Tools.printProgress( op, self.scenario.n_intermidiaries)
			_pos = 0
			_neg = 0
			for i in range(N): #scorro tutti gli accusatori i per un intermediario j
				_pos += matrix[i,j,POS]
				_neg += matrix[i,j,NEG]
			#self.scenario.Tscore[op] = (1.0+_pos)/(2.0+_pos+_neg)
			if self.scenario.isFraudster(j):
				logging.info(str(op)+' ,pos='+str(_pos)+', neg='+str(_neg)+', is fraudster')
			else:
				logging.info(str(op)+' ,pos='+str(_pos)+', neg='+str(_neg)+', is honest')


			#transactions[j-self.scenario.n_providers][POS] = _pos
			#transactions[j-self.scenario.n_providers][NEG] = _neg
		"""
	
		for i in range(self.scenario.n_providers): #scorro tutti gli originaotr
			for j in range(self.scenario.n_providers, N):
				op = j - self.scenario.n_providers
				_pos = matrix[i,j,POS]
				_neg = matrix[i,j,NEG]
				if _pos != 0 and _neg != 0:
					self.scenario.R2[i,op] = (1.0+_pos)/(2.0+_pos+_neg)
			

		for i in range(self.scenario.n_providers):
			#trovo max
			
			for j in range(self.scenario.n_providers, N):
				op = j - self.scenario.n_providers
				_pos = matrix[i,j,POS]
				_neg = matrix[i,j,NEG]
				if _pos == 0 and _neg == 0:
					trustedNode = max(self.scenario.R2[i,:])#wronng
					rep2 = self.scenario.R2[]
	
				
					






		


		print("calc threshold:")
		numeratore = 0
		denominatore = 0
		for i in range(self.scenario.n_intermidiaries):
			numeratore += self.scenario.Tscore[i] #*weights[i]
		denominatore =  self.scenario.n_intermidiaries #denominatore + weights[i]
		average = numeratore / denominatore
		x=0
		cnt = 0
		for  i in range(self.scenario.n_intermidiaries):
			#if Tscore[i+ProviderConfig.n_providers] > 0.5:
			cnt = cnt + 1
			x = x+(self.scenario.Tscore[i] - average)**2
		x = x / cnt
		standarddev = math.sqrt(x)
		threshold = average - standarddev #99%=2,58 95%=1.96
		print(threshold)
		if threshold < 0.5:
			threshold = 0.5


		print("compare threshold")
		for i in range(self.scenario.n_intermidiaries):
		
			if self.scenario.isFraudster(i+self.scenario.n_providers):
				if self.scenario.Tscore[i] < 0.5:
					#print("fraudster is: " + str(i+self.scenario.n_providers) + " with score values: " +  str(Tscore[i]) +"<"+str(threshold))
					self.scenario.fraudsters += 1

				if self.scenario.Tscore[i] > 0.5 and self.scenario.Tscore[i] < 0.9 and self.scenario.Tscore[i] < threshold:

					self.scenario.suspected_fraudsters += 1

				if self.scenario.Tscore[i] > 0.5 and self.scenario.Tscore[i] < 0.9 and self.scenario.Tscore[i] > threshold:
					
					self.scenario.suspected_falsenegative += 1

				if self.scenario.Tscore[i] >= 0.9:

					self.scenario.falsenegative += 1

				if self.scenario.Tscore[i] == 0.5:

					self.scenario.unknown_fraudsters += 1
			else:

				if self.scenario.Tscore[i] >= 0.9:

					self.scenario.honests += 1

				if self.scenario.Tscore[i] < 0.9 and self.scenario.Tscore[i] > 0.5 and self.scenario.Tscore[i] > threshold:
					
					self.scenario.suspected_honests += 1

				if self.scenario.Tscore[i] < 0.9 and self.scenario.Tscore[i] > 0.5 and self.scenario.Tscore[i] < threshold:

					self.scenario.suspected_falsepositive += 1

				if self.scenario.Tscore[i] < 0.5:

					self.scenario.falsepositive += 1

				if self.scenario.Tscore[i] == 0.5:

					self.scenario.unknown_honests += 1




		print("DEBUG disguised calls: " + str(self.scenario.disguised_behaviour))
		print("DEBUG malicious calls: " + str(self.scenario.malicious_behaviour))



		print("\nRESULT ON FRAUD DETECTION:  " + str(self.scenario.accusations_counter) +"/"+ str(self.scenario.accusations_counter_ref) + " accusations deficit" )

		print("\nRESULT ON FRAUDSTERS DETECTION: ")
		print(str(self.scenario.fraudsters)+ "/" + str(self.scenario.n_fraudsters)+ " fraudsters detected  ")
		print(str(self.scenario.suspected_fraudsters)+ "/" + str(self.scenario.n_fraudsters) +" fraudsters suspected,  ")
		print(str(self.scenario.suspected_falsenegative)+ "/" + str(self.scenario.n_fraudsters)+ " suspected  false negative,   ")
		print(str(self.scenario.falsenegative)+ "/" + str(self.scenario.n_fraudsters)+ " false negative,   ")
		print(str(self.scenario.unknown_fraudsters)   + "/" + str(self.scenario.n_fraudsters)+   " unknown fraudsters  ")
		print("\nRESULT ON DETECTION ERRORS: ")
		print(str(self.scenario.honests) + "/" + str(self.scenario.n_honests) + " honests,  ")
		print(str(self.scenario.suspected_honests) + "/" + str(self.scenario.n_honests) + " suspected honests,  ")
		print(str(self.scenario.suspected_falsepositive) + "/" + str(self.scenario.n_honests) + " suspected false positives,  ")			
		print(str(self.scenario.falsepositive) + "/" + str(self.scenario.n_honests) + " false positives,  ")
		print(str(self.scenario.unknown_honests)+ "/" + str(self.scenario.n_honests) + " unknown honests.  ")

		fx.flush()
		fx.close()

		"""

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

	'''
	def measure_fraudsters_behaviour(self, trace):
		for i in range(self.scenario.l_chain):
			ind=int(trace[Csv.TRANSIT+i])
			if self.scenario.isFraudster(ind):
				if not self.scenario.isFraud(int(trace[Csv.FRAUD])):
					self.disguised_behaviour += 1 #le transazioni buone fatte da un frodatre nel campione
				else:
					self.malicious_behaviour += 1 #le transazioni maligne fatte da un frodatre nel campione
	'''
	'''
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
	'''




		