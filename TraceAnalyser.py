import numpy as np
import h5py
import csv
from config import *
import random

class TraceAnalyser:




	def __init__(self, scenario,dataset):
		super(TraceAnalyser, self).__init__()
		self.scenario = scenario
		self.dataset = dataset





	def computeRevenue(self, node):
		fx = h5py.File(self.dataset.dataset, 'a')
		matrix = fx['fback_matrix']
		count=0

		print("\nParse call traces and create the feedback matrix.")
		revenue = 0
		for trace in traces:
			for i in range(self.scenario.l_chain):
				if node==int(trace[Csv.TRANSIT+i]):
					revenue += hasRevenue(node)
				
			


	def hasRevenue(self, node):

		termination_charges_international_pstn = 0.15 #local tariff 
		termination_charges_local_pstn = 0.10
		termination_charges_isp = 0.1 #international from ISPA to ISPB (international)
		#endogenous_charges = 0.1693


		if self.scenario.isFraudster(node):
			return (termination_charges_international_pstn-termination_charges_local_pstn)*TraceConfig.average_call_duration
		if self.scenario.isIntermidiary(node):
			return termination_charges_isp*TraceConfig.average_call_duration
		if self.scenario.isProvider(node):
			return termination_charges_international_pstn*TraceConfig.average_call_duration
		


