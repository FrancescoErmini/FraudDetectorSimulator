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

	def __init__(self, scenario):
		super(TrustMan, self).__init__()


		self.disguised_behaviour = 0
		self.malicious_behaviour = 0
		self.frauds_detector_counter = 0 #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
		self.frauds_detector_counter_ref = 0
		self.accusations_counter_ref = 0 #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
		self.accusations_counter = 0 #conta quante accuse vengono effettivamente fatte a casua della non risposta degli intermediari
		
		self.fraudsters = 0
		self.suspected_fraudsters = 0
		self.suspected_falsenegative = 0
		self.falsenegative = 0
		self.unknown_fraudsters = 0
		
		self.honests = 0
		self.suspected_honests = 0
		self.suspected_falsepositive = 0		
		self.falsepositive = 0
		self.unknown_honests = 0

		self.scenario = scenario
		self.fraudBehaviour = 0
		self.accusationsAnalyzed = 0
		self.fraudsAnalyzed = 0

		self.fraudsters_detection = 0
		self.fraudsters_detection_error = 0
		self.fraudsters_detection_missing = 0
		self.honests_detection_error  = 0



	def updateMatrix(self, infile, data_out):

		
		#logging.basicConfig(filename=logfile,level=logging.DEBUG)

		N = self.scenario.n_providers + self.scenario.n_intermidiaries
		POS = 0 #const
		NEG = 1 #const
		
		#M = [[[0 for k in range(2)] for j in range(N)] for i in range(N)]
		"""
		with h5py.File(outfile, "a") as f:
			f.create_dataset("fback_matrix", shape=(N,N,2))
			f.create_dataset("normal_matrix", shape=(N,N))
			f.create_dataset("opinion_matrix", shape=(N,N,4))
			f.create_dataset("trust_score", shape=(N,1))
		"""

		fx = h5py.File(self.scenario.dataset, 'a')
		matrix = fx[data_out]


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

				if self.scenario.isFraud(trace[Csv.FRAUD]):
						self.frauds_detector_counter_ref += 1


				for i in range(self.scenario.l_chain):
					ind=int(trace[Csv.TRANSIT+i])					
					if self.scenario.isFraudster(ind):
						if not self.scenario.isFraud(trace[Csv.FRAUD]):
							self.disguised_behaviour += 1 #le transazioni buone fatte da un frodatre nel campione
						else:
							self.malicious_behaviour += 1 #le transazioni maligne fatte da un frodatre nel campione

				if self.scenario.isCoopProvider(trace[Csv.TERMIN]) and not self.scenario.isFraud(trace[Csv.FRAUD]):
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
				if self.scenario.isCoopProvider(trace[Csv.TERMIN]) and self.scenario.isFraud(trace[Csv.FRAUD]):
					
					self.frauds_detector_counter += 1
					self.accusations_counter_ref += 1 #self.scenario.l_chain
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
						self.accusations_counter_ref += 1
						if self.scenario.isCoopIntermidiary(source):
							self.accusations_counter += 1
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
						
		print("Matrix updated..")


		self.fraudBehaviour = 100*self.malicious_behaviour/(self.malicious_behaviour+self.disguised_behaviour)
		self.accusationsAnalyzed = (100*self.accusations_counter)/self.accusations_counter_ref #tasso di risposta per nodi transizione nel campione
		self.fraudsAnalyzed = (100*self.frauds_detector_counter)/self.frauds_detector_counter_ref #tasso di frodi conosciute (rilevate) nel campione




	
	def fraudsterClassifier(self, data_in, outfile):



		dataset = h5py.File(self.scenario.dataset, 'r')
		trust_scores = dataset['trust_score'][self.scenario.n_providers:self.scenario.N,0]

		avg = np.mean(trust_scores)
		std = np.std(trust_scores)

		threshold = avg - std

		if threshold < 0.5:
			threshold = 0.5

		print("compare threshold")
		for i in range(self.scenario.n_intermidiaries):
		
			if self.scenario.isFraudster(i+self.scenario.n_providers):
				if trust_scores[i] < 0.5:
					#print("fraudster is: " + str(i+self.scenario.n_providers) + " with score values: " +  str(Tscore[i]) +"<"+str(threshold))
					self.fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < 0.9 and trust_scores[i] < threshold:

					self.suspected_fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < 0.9 and trust_scores[i] > threshold:
					
					self.suspected_falsenegative += 1

				if trust_scores[i] >= 0.9:

					self.falsenegative += 1

				if trust_scores[i] == 0.5:

					self.unknown_fraudsters += 1
			else:

				if trust_scores[i] >= 0.9:

					self.honests += 1

				if trust_scores[i] < 0.9 and trust_scores[i] > 0.5 and trust_scores[i] > threshold:
					
					self.suspected_honests += 1

				if trust_scores[i] < 0.9 and trust_scores[i] > 0.5 and trust_scores[i] < threshold:

					self.suspected_falsepositive += 1

				if trust_scores[i] < 0.5:

					self.falsepositive += 1

				if trust_scores[i] == 0.5:

					self.unknown_honests += 1
	
		self.fraudsters_detection = 100.0 * self.fraudsters / self.scenario.n_fraudsters
		self.fraudsters_detection_error = 100.0 * self.falsenegative / self.scenario.n_fraudsters
		self.fraudsters_detection_missing = 100.0 * self.unknown_fraudsters /self.scenario.n_fraudsters
		self.honests_detection_error = 100.0 * self.falsepositive / self.scenario.n_honests


		