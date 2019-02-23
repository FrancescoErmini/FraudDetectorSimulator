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

	file_path=''

	"""docstring for TrustManager"""
	def __init__(self, trace_source):
		super(TrustManager, self).__init__()
		self.trace_source = trace_source

		with h5py.File("data/matrix.hdf5", "a") as f:
        	f.create_dataset("bigM", shape=(N,N, 2), dtype=np.uint8)

	def updateMatrix():
        
        fx = h5py.File('matrix.hdf5', 'a')
        matrix = fx['bigM']

        for file in file_json:

            with open(file) as f:
                data = json.load(f)
            traces = data["traces"]

            for trace in traces:

                count = count + 1

                if count > max_calls:
                    print("ANALYSIS STOPPED AT: " + str(count))
                    return


                if TraceConfig.fraudsters_camouflage:
                    for i in range(len(trace["transit"])):
                        if trace["transit"][i]["id"] in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                            if trace["fraud"]==0:
                                good = good + 1 #le transazioni buone fatte da un frodatre nel campione
                            else:
                                bad = bad + 1 #le transazioni maligne fatte da un frodatre nel campione
                else:
                    bad = 100

                if trace["fraud"]==0 and trace["termin"] in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                    #print("+")
                    origin = trace["origin"]
                    nextop = trace["transit"][0]["id"]
                    #M[origin][nextop][0] = M[origin][nextop][0] + 1
                    matrix[origin,nextop,0]=matrix[origin,nextop,0] + 1
                    for i in range(len(trace["transit"])-1):
                        source = trace["transit"][i]["id"]
                        target = trace["transit"][i+1]["id"]
                        if source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                            #M[source][target][0] = M[source][target][0] + 1
                            matrix[source,target,0] = matrix[source,target,0] + 1
                            if TrustConfig.ref:
                                Ref[source][target] = Ref[source][target] +1

                if trace["fraud"]==1 and trace["termin"] in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                    frauds_counter = frauds_counter + 1
                    origin = trace["origin"]
                    nextop = trace["transit"][0]["id"]
                    #M[origin][nextop][1] = M[origin][nextop][1] + 1
                    matrix[origin,nextop,1]=matrix[origin,nextop,1] + 1
                    if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and nextop not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and matrix[origin][nextop][1]>0:
                            #M[origin][nextop][1] = M[origin][nextop][1] - 1
                            matrix[origin,nextop,1]=matrix[origin,nextop,1] - 1
                    for i in range(len(trace["transit"])-1):
                        source = trace["transit"][i]["id"]
                        target = trace["transit"][i+1]["id"]
                        reports_counter_ref = reports_counter_ref + 1
                        if source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                            reports_counter = reports_counter + 1
                            #M[source][target][1] = M[source][target][1] + 1
                            matrix[source,target,1] = matrix[source,target,1] + 1
                            Revenue[target] = Revenue[target] +  TrustManager.calcRevenue(trace)
                            if TrustConfig.ref:
                                Ref[source][target] = Ref[source][target] +1
                            if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and matrix[source][target][1]>0:  
                                #M[source][target][1] = M[source][target][1] -  1.0 / (i+2)
                                matrix[source,target,1] = matrix[source,target,1] -  1.0 / (i+2)
                            if TrustConfig.symmetry_strategy and matrix[target][source][1]>=1:  
                                #M[source][target][1] = M[source][target][1] - 1
                                #M[target][source][1] = M[target][source][1] - 1
                                matrix[source,target,1] = matrix[source,target,1] -  1
                                matrix[target,source,1] = matrix[target,source,1] -  1
        print("stop read traces.")
        fx.flush()
        fx.close()
		