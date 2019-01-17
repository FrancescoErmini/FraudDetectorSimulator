#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from TraceGeneretor import TraceGeneretor
from TrustManager import TrustManager
from config import ProviderConfig, TraceConfig, TrustConfig, FraudStrategy, FraudType, TarifConfig, Result
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import math

#import scipy.optimize as opt;


def main():
	n_iteration = 10
	minute  = 0
	n_call = 4666 #416400 #41666 # 10 MIN
	n_call_fraud = 283 #20820 #1000 #2083 # 10 min 5%

	fraudrevenues= []
	fraudrevenues_abs = []
	fraudetection = []
	falsepositives = []
	falsenegatives = []
	x = [0 for i in range(1+n_iteration)]
	y = [0 for i in range(1+n_iteration)]
	c = 0

	
	go = False

	if not go:
		TraceGeneretor.generateCalls(n_call,n_call_fraud)

		res = TrustManager.computeTrust()
		print("fraud="+str(res[0])+" detect="+str(res[1])+" pFp="+str(res[2])+" pFN="+str(res[3])+" avRev="+str(res[4]))
	

	if go:
		max_call_fraud = (n_call*30)/100
		#for i in range((n_call*30)/100, -(n_call/n_iteration), -(n_call/n_iteration)):
		for i in range(100, max_call_fraud, max_call_fraud/n_iteration):
       # v = [pFraud, pDetect, pFalsepositive, pFalsenegative,  fraudAverageRevenue, fraudsters]

			TraceGeneretor.generateCalls(n_call,i)
			res = TrustManager.computeTrust()

			falsepositives.append([res[0], res[4] ] )
			fraudetection.append([res[0], res[1]])

			falsenegatives.append([res[0], res[5] ] )
			fraudrevenues.append([res[0], res[3]])

			print("p fraud="+str(res[0])+" p detect="+str(res[1])+" p fp="+str(res[2])+" p fn ="+str(res[3])+" fraudRevAVG="+str(res[5]))



		if Result.graphB:
			fig, ax = plt.subplots()
			ax.scatter(*zip(*fraudetection_error), s=10,c='r', marker="s", label='fp')
			ax.scatter(*zip(*falsenegatives), s=10, c='g', marker="s", label='fn')
			plt.xlim(100, 0) 
			plt.ylim(0, 100) 
			ax.set_ylabel('P error detention [%]')
			ax.set_xlabel('P fraud [%]')
			ax.set_title('Minimize detection error by varying threshold dev='+str(std))
			#ax.set_xticks(ind+width/4)
			#plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
			plt.legend(loc='upper right')
			plt.show()
		

			#print("fraud="+str(100.0-res[0])+" detect="+str(res[1])+" revenue="+str(res[3])+" fp="+str(res[4])+" fn="+str(res[5])+" avRev="+str(res[6]))
		
		#res = [fraud_behaviour, fraudstersPercentage, RevenuePercentage, Loss, falsepositivePercentage, falsenegativePercentage]
		
		if Result.graphA:
			fig, ax = plt.subplots()
			ax.scatter(*zip(*fraudrevenues), s=5, c='b', marker="s", label='revenue')
			ax.scatter(*zip(*fraudetection), s=5, c='r', marker="o", label='detention')
			ax.scatter(*zip(*falsenegatives), s=10, c='g', marker="s", label='fn')
			plt.xlim(100, 0) 
			plt.ylim(0, 100) 
			ax.set_ylabel('P detention [%]')
			ax.set_xlabel('P fraud [%]')
			ax.set_title('Maximizing fraud profitability by varying fraud probability')
		    #ax.set_xticks(ind+width/4)
			#plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
			plt.legend(loc='upper right')
			plt.show()

		if Result.graphC:
			fig, ax = plt.subplots()
			ax.scatter(*zip(*fraudrevenues_abs), s=5, c='b', marker="s", label='abs revenue')
			ax.scatter(*zip(*fraudetection), s=5, c='r', marker="o", label='detention')
			ax.scatter(*zip(*falsepositives), s=10, c='g', marker="s", label='fn')
			plt.xlim(100, 0) 
			plt.ylim(0, 100) 
			ax.set_ylabel('Fraud Revenue[%]')
			ax.set_xlabel('P fraud [%]')
			ax.set_title('Fraud absolute profitability by varying fraud probability')
		    #ax.set_xticks(ind+width/4)
			#plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
			plt.legend(loc='upper right')
			plt.show()
		

		
		
		

if __name__== "__main__":
  main()

#revenue è la percentuale che esprime quanto in percentuale il frodatore ha guadagnato rispetto al guadagno che avrebbe fatto se non fosse stato individuato