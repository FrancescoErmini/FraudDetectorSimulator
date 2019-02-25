#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import math
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib
#import pandas as pd
#import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
#matplotlib.style.use('ggplot')
#from pandas import DataFrame
from config import ProviderConfig, TraceConfig, TrustConfig, FraudStrategy, FraudType, Result
import jsonlines


class TrustManager:
	""" input values """
	infile=''
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

	def __init__(self, providers, intermidiaries, fraudsters_percentage, l_chain, calls, frauds_percentage, provider_participation
		, intermidiaries_participation):
		super(TrustManager, self).__init__()
		self.infile=infile
		self.n_providers = providers
		self.n_intermidiaries = intermidiaries 
		self.n_fraudsters = intermidiaries * fraudsters_percentage // 100
		self.l_chain=l_chain
		self.n_calls = calls
		self.n_calls_fraud = calls * frauds_percentage // 100
		self.frauds_percentage = frauds_percentage
		self.n_coop_providers = provider_participation*providers//100
		self.n_coop_intermidiaries = intermidiaries_participation*intermidiaries//100
      


	def updateMatrix(self, traces_file):

		POS = 0 #const
		NEG = 1 #const
		N = self.n_providers + self.n_intermidiaries
		
		with h5py.File("data/matrix.hdf5", "a") as f:
        	f.create_dataset("bigM", shape=(N,N, 2), dtype=np.uint8)
        
        fx = h5py.File('matrix.hdf5', 'a')
        matrix = fx['bigM']


		with open(traces_file, 'r') as f:
			reader = csv.reader(f)
			traces = list(reader)

        	for trace in traces:
        		'''
                count = count + 1

                if count > max_calls:
                    print("ANALYSIS STOPPED AT: " + str(count))
                    return
				'''

				measure_fraudsters_behaviour(self, trace):

                if isCoopProvider(trace[Csv.TERMIN]) and not isFraud(trace[Csv.FRAUD]) # in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                    origin = trace[Csv.ORIGIN]
                    nextop = trace[Csv.TRANSIT]
                    matrix[origin,nextop,POS]=matrix[origin,nextop,POS] + 1
                    for i in range(self.l_chain-1):
                        source = trace[Csv.TRANSIT+i]
                        target = trace[Csv.TRANSIT+i+1]
                        if isCoopIntermidiary(source):
                            #M[source][target][0] = M[source][target][0] + 1
                            matrix[source,target,POS] = matrix[source,target,POS] + 1
                            if TrustConfig.ref:
                                Ref[source][target] = Ref[source][target] +1

                if isCoopProvider(trace[Csv.TERMIN]) and isFraud(trace[Csv.FRAUD]):
                    self.frauds_detector_counter += 1
                    origin = trace[Csv.ORIGIN]
                    nextop = trace[Csv.TRANSIT]
                    #M[origin][nextop][1] = M[origin][nextop][1] + 1
                    matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] + 1
                    if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and not isFraudster(nextop) and matrix[origin][nextop][NEG]>0: #condizione sul valore positivo serve a evitare di avere valori negativi
                            #M[origin][nextop][1] = M[origin][nextop][1] - 1
                            matrix[origin,nextop,NEG]=matrix[origin,nextop,NEG] - 1
                    for i in range(self.l_chain-1):
                        source = trace[Csv.TRANSIT+i]
                        target = trace[Csv.TRANSIT+i+1]
                        self.accusations_counter_ref += 1
                        if isCoopIntermidiary(source): #source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                            self.accusations_counter += 1
                            #M[source][target][1] = M[source][target][1] + 1
                            matrix[source,target,NEG] = matrix[source,target,NEG] + 1
                            Revenue[target] = Revenue[target] +  TrustManager.calcRevenue(trace)
                            if TrustConfig.ref:
                                Ref[source][target] = Ref[source][target] +1
                            if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and matrix[source][target][1]>0:  
                                #M[source][target][1] = M[source][target][1] -  1.0 / (i+2)
                                matrix[source,target,NEG] = matrix[source,target,NEG] -  1.0 / (i+2)
                            if TrustConfig.symmetry_strategy and matrix[target,source,NEG]>=1:  
                                #M[source][target][1] = M[source][target][1] - 1
                                #M[target][source][1] = M[target][source][1] - 1
                                matrix[source,target,NEG] = matrix[source,target,NEG] -  1
                                matrix[target,source,NEG] = matrix[target,source,NEG] -  1
        print("stop read traces.")
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
    	if index in range(self.n_providers+self.n_intermidiaries-self.n_fraudsters, self.n_providers+self.n_intermidiaries):
    		return True 
    	else:
    		return False

    def isFraud(self, value):
    	if value == 1:
    		return True
    	else:
    		return False

   	def isCoopProvider(self, index):
   		if index in range(self.n_providers/2-self.n_coop_providers/2, self.n_providers/2 + self.n_coop_providers/2):
   			return True
   		else:
   			return False

   	def isCoopIntermidiary(self, index):
   		if index in range(self.n_providers+(self.n_intermidiaries-self.n_fraudsters)/2-self.n_coop_intermidiaries/2,self.n_providers+(self.n_intermidiaries-self.n_fraudsters)/2+self.n_coop_intermidiaries/2):
   			return True
   		else:
   			return False

   	def measure_fraudsters_behaviour(self, trace):
	    if TraceConfig.fraudsters_camouflage:
            for transit_th in range(self.l_chain):
                if self.isFraudster(trace[Csv.TRANSIT+transit_th]) # in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                    if not self.isFraud(trace[Csv.FRAUD]):
                        self.disguised_behaviour += 1 #le transazioni buone fatte da un frodatre nel campione
                    else:
                        self.malicious_behaviour += 1 #le transazioni maligne fatte da un frodatre nel campione
        else:
        	self.disguised_behaviour = 0
            self.malicious_behaviour = self.n_calls_fraud


    def calcRevenue(trace):
        r_bypass = (trace["rateA"]-trace["rateB"])*trace["durationA"]
        #r_bypass = FraudType.bypass_revenue * trace["durationA"]
        r_fas = (trace["durationA"] - trace["durationB"])*trace["rateA"]
        r_lrn = (trace["rateB"]-trace["rateA"])*trace["durationA"]
        r = 0

        if FraudType.fas_fraud:
            r = r_fas
        if FraudType.bypass_fraud:
            r = r_bypass
        if FraudType.bypass_fraud and FraudType.fas_fraud:
            r = r_bypass + r_fas
        if FraudType.lrn_fraud:
            r = r_lrn




		