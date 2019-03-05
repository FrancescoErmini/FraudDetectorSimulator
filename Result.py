import numpy as np
import h5py
import csv
from config import *

class Result:



	def __init__(self, scenario, manager):
		super(Result, self).__init__()
		self.scenario = scenario
		self.manager = manager





	def printRes(self):

		print("SIM CONFIG")
		print("calls: "+ str(self.scenario.n_calls))
		print("fraud calls: " + str(self.scenario.n_calls_fraud))
		print("coop. providers: " + str(self.scenario.n_coop_providers)+"/"+str(self.scenario.n_providers))
		print("coop. intermidiaries: " + str(self.scenario.n_coop_intermidiaries)+"/"+str(self.scenario.n_intermidiaries))

		print("simmetry strategy: " + str(TrustConfig.simmetry_strategy))
		print("pretrust strategy: " + str(TrustConfig.pretrust_strategy) + " with " + str(TrustConfig.l_cascade_agreements)+"/"+str(self.scenario.l_chain))
		print("fraudster behaviour: " + str(self.manager.fraudBehaviour))




		print("\nRAW RESULT ON FRAUDSTERS: ")
		print(str(self.manager.fraudsters)+ "/" + str(self.scenario.n_fraudsters)+ " fraudsters detected  ")
		print(str(self.manager.suspected_fraudsters)+ "/" + str(self.scenario.n_fraudsters) +" fraudsters suspected,  ")
		print(str(self.manager.suspected_falsenegative)+ "/" + str(self.scenario.n_fraudsters)+ " suspected  false negative,   ")
		print(str(self.manager.falsenegative)+ "/" + str(self.scenario.n_fraudsters)+ " false negative,   ")
		print(str(self.manager.unknown_fraudsters)   + "/" + str(self.scenario.n_fraudsters)+   " unknown fraudsters  ")
		print("\nRAW RESULT ON honests: ")
		print(str(self.manager.honests) + "/" + str(self.scenario.n_honests) + " honests,  ")
		print(str(self.manager.suspected_honests) + "/" + str(self.scenario.n_honests) + " suspected honests,  ")
		print(str(self.manager.suspected_falsepositive) + "/" + str(self.scenario.n_honests) + " suspected false positives,  ")			
		print(str(self.manager.falsepositive) + "/" + str(self.scenario.n_honests) + " false positives,  ")
		print(str(self.manager.unknown_honests)+ "/" + str(self.scenario.n_honests) + " unknown honests.  ")


		print("\nSTAT RESULT:")

		print("frauds detected: " + str(self.manager.fraudsAnalyzed))
		print("accusations analized: " + str(self.manager.accusationsAnalyzed))

		print("fraudsters_detection: " + str(self.manager.fraudsters_detection))
		print("fraudsters_detection_error: " + str(self.manager.fraudsters_detection_error))
		print("fraudsters_detection_missing: " + str(self.manager.fraudsters_detection_missing))
		print("honests detected error: " + str(self.manager.honests_detection_error))

	def storeRes(self, outfile):

		with open(outfile, "w") as text_file:
				print(f"fraudsters detected: {self.manager.fraudsters_detection}", file=text_file)
				print(f"fraudsters detected error: {self.manager.fraudsters_detection_error}", file=text_file)
				print(f"fraudsters detected missing: {self.manager.fraudsters_detection_missing}", file=text_file)
				print(f"honests detected error: {self.manager.honests_detection_error}", file=text_file)




	def printRawTrustVector(self):
		dataset = h5py.File(self.scenario.dataset, 'a')
		res = dataset['trust_score'][:]
		print(res[self.scenario.n_providers:self.scenario.N,0])

	def store2Csv(self, file):
		dataset = h5py.File(self.scenario.dataset, 'a')
		trust_scores = dataset['trust_score'][:]
		with open(file, mode='w') as info:
			writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(["id", "trust_score"])
			for i in range(self.scenario.n_providers,self.scenario.n_providers + self.scenario.n_intermidiaries):
				writer.writerow([i, trust_scores[i][0]])
		