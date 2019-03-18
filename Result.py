import numpy as np
import h5py
import csv
from config import *
import random

class Result:




	def __init__(self, scenario,dataset, manager):
		super(Result, self).__init__()
		self.scenario = scenario
		self.dataset = dataset
		self.manager = manager

		self.fraudsters_tot = 0
		self.honests_tot = 0
		#valori assoluti
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

		#valori percentuali
		
		self.fraudsters_detection = 0
		self.fraudsters_detection_suspect = 0
		self.fraudsters_detection_error = 0
		self.fraudsters_detection_missing = 0

		self.honests_detection = 0
		self.honests_detection_suspect = 0
		self.honests_detection_error  = 0
		self.honests_detection_missing = 0


		self.threshold = 0
		"""

		self.disguised_behaviour = manager.disguised_behaviour
		self.malicious_behaviour = manager.malicious_behaviour
		self.frauds_detector_counter = manager.frauds_detector_counter #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
		self.frauds_detector_counter_ref = manager.frauds_detector_counter_ref
		self.accusations_counter_ref = manager.accusations_counter_ref #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
		self.accusations_counter = manager.accusations_counter #conta quante accuse vengono effettivamente fatte a casua della non risposta degli intermediari
		
		self.fraudBehaviour = manager.fraudBehaviour
		self.accusationsAnalyzed = manager.accusationsAnalyzed
		self.fraudsAnalyzed = manager.fraudsAnalyzed
		"""
	'''
	def fraudsterClassifier(self, targets, trust_scores):

		avg = np.mean(trust_scores)
		std = np.std(trust_scores)

		self.threshold = avg - std

		if self.threshold < 0.5:
			self.threshold = 0.5

		#print("\nClassifying peers into fraudsters and honests using trust scores.")
		for i in range(len(targets)):
		
			if self.scenario.isFraudster(i):
				self.fraudsters_tot += 1
		
				if trust_scores[i] < 0.5:
					#print("fraudster is: " + str(i+self.scenario.n_providers) + " with score values: " +  str(Tscore[i]) +"<"+str(self.threshold))
					self.fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < TNSLAsettings.trustee_score and trust_scores[i] < self.threshold:

					self.suspected_fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < TNSLAsettings.trustee_score and trust_scores[i] > self.threshold:
					
					self.suspected_falsenegative += 1

				if trust_scores[i] >= TNSLAsettings.trustee_score:

					self.falsenegative += 1

				if trust_scores[i] == 0.5:

					self.unknown_fraudsters += 1
			else:
				self.honests_tot += 1
				if trust_scores[i] >= TNSLAsettings.trustee_score:

					self.honests += 1

				if trust_scores[i] < TNSLAsettings.trustee_score and trust_scores[i] > 0.5 and trust_scores[i] > self.threshold:
					
					self.suspected_honests += 1

				if trust_scores[i] < TNSLAsettings.trustee_score and trust_scores[i] > 0.5 and trust_scores[i] < self.threshold:

					self.suspected_falsepositive += 1

				if trust_scores[i] < 0.5:

					self.falsepositive += 1

				if trust_scores[i] == 0.5:

					self.unknown_honests += 1
	
		self.fraudsters_detection = 100.0 * self.fraudsters / self.scenario.n_fraudsters
		self.fraudsters_detection_suspect =  100.0 * (self.suspected_fraudsters+self.suspected_falsenegative) / self.scenario.n_fraudsters
		self.fraudsters_detection_error = 100.0 * (self.falsenegative) / self.scenario.n_fraudsters
		self.fraudsters_detection_missing = 100.0 * self.unknown_fraudsters / self.scenario.n_fraudsters
		
		self.honests_detection = 100.0 * self.honests / self.scenario.n_honests
		self.honests_detection_suspect = 100.0 * (self.suspected_honests+self.suspected_falsepositive) / self.scenario.n_honests
		self.honests_detection_error  = 100.0 * self.falsepositive / self.scenario.n_honests
		self.honests_detection_missing = 100.0 * self.unknown_honests / self.scenario.n_honests

	'''


	def fraudsterClassifier2(self, target, trust_score):
		i = target
		
		if self.scenario.isFraudster(target):
			
			self.fraudsters_tot += 1
			if trust_score < 0.5:
				#print("fraudster is: " + str(i+self.scenario.n_providers) + " with score values: " +  str(Tscore[i]) +"<"+str(self.threshold))
				self.fraudsters += 1

			if trust_score > 0.5 and trust_score < TNSLAsettings.trustee_score:

				self.suspected_fraudsters += 1				

			if trust_score >= TNSLAsettings.trustee_score:

				self.falsenegative += 1

			if trust_score == 0.5:

				self.unknown_fraudsters += 1
		else:
			self.honests_tot += 1

			if trust_score >= TNSLAsettings.trustee_score:

				self.honests += 1

			if trust_score < TNSLAsettings.trustee_score and trust_score > 0.5:
				
				self.suspected_honests += 1

			if trust_score < 0.5:

				self.falsepositive += 1

			if trust_score == 0.5:

				self.unknown_honests += 1

		res = False
		if trust_score < 0.5:
			res = True
		return res



	def printRes(self):

		print("\nSIM CONFIG")
		print("calls: "+ str(self.scenario.n_calls))
		print("fraud calls: " + str(self.scenario.n_calls_fraud))
		print("coop. providers: " + str(self.scenario.n_coop_providers)+"/"+str(self.scenario.n_providers))
		print("coop. intermidiaries: " + str(self.scenario.n_coop_intermidiaries)+"/"+str(self.scenario.n_honests))
		print("simmetry strategy: " + str(TrustConfig.simmetry_strategy))
		print("pretrust strategy: " + str(TrustConfig.pretrust_strategy) + " with " + str(TrustConfig.l_cascade_agreements)+"/"+str(self.scenario.l_chain))
		
		print("\nTRACE ANALISYS")
		print("fraudster behaviour: " + str(self.manager.fraudBehaviour)+"%")
		print("frauds detected: " + str(self.manager.fraudsAnalyzed)+"%")
		print("accusations analized: " + str(self.manager.accusationsAnalyzed)+"%")

		
		print("fraud detector counter "  + str(self.manager.frauds_detector_counter))
		print("fraud detector counter ref " + str(self.manager.frauds_detector_counter_ref))
		print("accusations counter: " + str(self.manager.accusations_counter))
		print("accusations counter ref: " + str(self.manager.accusations_counter_ref))
		print("transaction counter: " + str(self.manager.transactions_counter ))



		print("\nRAW RESULT ON FRAUDSTERS: ")
		print(str(self.fraudsters)+ "/" + str(self.fraudsters_tot)+ " fraudsters detected  ")
		print(str(self.suspected_fraudsters)+ "/" + str(self.fraudsters_tot) +" fraudsters suspected,  ")
		#print(str(self.suspected_falsenegative)+ "/" + str(self.fraudsters_tot)+ " suspected  false negative,   ")
		print(str(self.falsenegative)+ "/" + str(self.fraudsters_tot)+ " false negative,   ")
		print(str(self.unknown_fraudsters)   + "/" + str(self.fraudsters_tot)+   " unknown fraudsters  ")
		print("\nRAW RESULT ON honests: ")
		print(str(self.honests) + "/" + str(self.honests_tot) + " honests,  ")
		print(str(self.suspected_honests) + "/" + str(self.honests_tot) + " suspected honests,  ")
		#print(str(self.suspected_falsepositive) + "/" + str(self.honests_tot) + " suspected false positives,  ")			
		print(str(self.falsepositive) + "/" + str(self.honests_tot) + " false positives,  ")
		print(str(self.unknown_honests)+ "/" + str(self.honests_tot) + " unknown honests.  ")
		'''
		print("\nSTAT RESULT:")
		print("fraudsters detection: "+str(self.fraudsters_detection))
		print("fraudsters detection suspect: "+str(self.fraudsters_detection_suspect))
		print("fraudsters detection error: "+str(self.fraudsters_detection_error))
		print("fraudsters detection missing: "+str(self.fraudsters_detection_missing))
		
		print("honests detection: "+str(self.honests_detection))
		print("honests detection suspect: "+str(self.honests_detection_suspect))
		print("honests detection error: "+str(self.honests_detection_error))
		print("honests detection missing: "+str(self.honests_detection_missing))
		'''


	def storeStat(self, file):

		with open(file, "w") as text_file:
				
				print(f"\nSIM CONFIG", file=text_file)
				print(f"providers:  {str(self.scenario.n_providers)}", file=text_file)
				print(f"intermidiaries: {str(self.scenario.n_intermidiaries)}", file=text_file)
				print(f"fraudsters: {str(self.scenario.n_fraudsters)} [{self.scenario.fraudsters_percentage}%]", file=text_file)

				print(f"calls:  {str(self.scenario.n_calls)}", file=text_file)
				print(f"fraud calls: {str(self.scenario.n_calls_fraud)} [{self.scenario.frauds_percentage}%]", file=text_file)

				print(f"coop. providers: {str(self.scenario.n_coop_providers)} / {str(self.scenario.n_providers)} [{self.scenario.provider_participation}%]", file=text_file)
				print(f"coop. intermidiaries: {str(self.scenario.n_coop_intermidiaries)} / {str(self.scenario.n_honests)} [{self.scenario.intermidiaries_participation}%]", file=text_file)
				print(f"simmetry strategy: {str(TrustConfig.simmetry_strategy)}", file=text_file)
				print(f"pretrust strategy: {str(TrustConfig.pretrust_strategy)} with {str(TrustConfig.l_cascade_agreements)} / {str(self.scenario.l_chain)}", file=text_file)
				
				print(f"\nTRACE ANALISYS", file=text_file)
				'''
				self.frauds_detector_counter = 0 #conta quante chiamate con frode sono effettivamente valutate a casusa della non risposta del terminator
		self.frauds_detector_counter_ref = 0
		self.accusations_counter_ref = 0 #conta quante accuse dovrebbero essere fatte nel sottoinsieme delle chiamate con frode rilevate
		self.accusations_counter = 0 #co
				'''
				print(f"fraud detector counter: {str(self.manager.frauds_detector_counter)}", file=text_file)
				print(f"fraud detector counter ref: {str(self.manager.frauds_detector_counter_ref)}", file=text_file)
				print(f"accusations counter: {str(self.manager.accusations_counter)}", file=text_file)
				print(f"accusations counter ref: {str(self.manager.accusations_counter_ref)}", file=text_file)

				print(f"fraudster behaviour: {str(self.manager.fraudBehaviour)}%", file=text_file)
				print(f"frauds detected: {str(self.manager.fraudsAnalyzed)}%", file=text_file)
				print(f"accusations analized: {str(self.manager.accusationsAnalyzed)}%", file=text_file)


				
				print(f"\nRAW RESULT ON FRAUDSTERS: ", file=text_file)
				print(f"{str(self.manager.fraudsters)} / {str(self.scenario.n_fraudsters)} fraudsters detected", file=text_file)
				print(f"{str(self.manager.suspected_fraudsters)} / {str(self.scenario.n_fraudsters)} fraudsters suspected", file=text_file)
				print(f"{str(self.manager.suspected_falsenegative)} / {str(self.scenario.n_fraudsters)}  suspected  false negative", file=text_file)
				print(f"{str(self.manager.falsenegative)} / {str(self.scenario.n_fraudsters)}  false negative", file=text_file)
				print(f"{str(self.manager.unknown_fraudsters)} / {str(self.scenario.n_fraudsters)} unknown fraudsters", file=text_file)
				print("\nRAW RESULT ON honests: ", file=text_file)
				print(f"{str(self.manager.honests)} / {str(self.scenario.n_honests)}  honests.", file=text_file)
				print(f"{str(self.manager.suspected_honests)} / {str(self.scenario.n_honests)} suspected honests.", file=text_file)
				print(f"{str(self.manager.suspected_falsepositive)} / {str(self.scenario.n_honests)} suspected false positives.", file=text_file)			
				print(f"{str(self.manager.falsepositive)} / {str(self.scenario.n_honests)} false positives.", file=text_file)
				print(f"{str(self.manager.unknown_honests)} / {str(self.scenario.n_honests)} unknown honests.", file=text_file)


				print(f"\nSTAT RESULT:", file=text_file)
				print(f"fraudsters detection: {str(self.manager.fraudsters_detection)}%", file=text_file)
				print(f"fraudsters detection suspect: {str(self.manager.fraudsters_detection_suspect)}%", file=text_file)
				print(f"fraudsters detection error: {str(self.manager.fraudsters_detection_error)}%", file=text_file)
				print(f"fraudsters detection missing: {str(self.manager.fraudsters_detection_missing)}%", file=text_file)
				
				print(f"honests detection: {str(self.manager.honests_detection)}%", file=text_file)
				print(f"honests detection suspect: {str(self.manager.honests_detection_suspect)}%", file=text_file)
				print(f"honests detection error: {str(self.manager.honests_detection_error)}%", file=text_file)
				print(f"honests detection missing: {str(self.manager.honests_detection_missing)}%", file=text_file)

	def printTrustScores(self,data_in):

		dataset = h5py.File(self.dataset.dataset, 'a')
		trust_scores = dataset['trust_scores'][self.scenario.n_providers:self.scenario.N,0]
		#print(trust_scores)
		print("\nPrint 3 random honest trust score: ")
		for i in range(3):
			rnd_honest_node = random.randint(0,self.scenario.n_honests-1)
			print(trust_scores[rnd_honest_node])

		print("Print 3 random fraud trust score: ")
		for i in range(3):
			rnd_fraudster_node = random.randint(self.scenario.n_honests, self.scenario.n_honests + self.scenario.n_fraudsters-1)
			print(trust_scores[rnd_fraudster_node])

	def printFeedback(self, targets):
		dataset = h5py.File(self.dataset.dataset, 'a')
		#random.seed(9001)

		
		for target in targets:

			#j = random.randint(self.scenario.n_providers,self.scenario.n_providers+self.scenario.n_honests-1)

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset['fback_matrix_updated'][::,target:target+1]
			
			pos = 0
			neg = 0
			for i in range(self.scenario.N):

				pos += fback_matrix_chunk[i][0][0]
				neg += fback_matrix_chunk[i][0][1]
			if self.scenario.isFraudster(target):
				print("fraudster="+str(target)+" has "+ str(pos) + " pos and " + str(neg) + " neg")
			else:
				print("honest="+str(target)+" has "+ str(pos) + " pos and " + str(neg) + " neg")
		
		
	def getFraudBehaviour(self):
		return self.manager.fraudBehaviour

	def printTrustAvg(self, targets, trust_scores):
		honests_counter = 0
		honests_score = 0
		fraudsters_counter = 0
		fraudsters_score = 0

		for i in range(len(targets)):
			if self.scenario.isFraudster(targets[i]):
				fraudsters_counter += 1
				fraudsters_score += trust_scores[i]
			else:
				honests_counter += 1
				honests_score += trust_scores[i]
		honests_score_avg = honests_score / honests_counter
		fraudsters_score_avg = fraudsters_score / fraudsters_counter
		print("honests avg trust score: " + str(honests_score_avg))
		print("fraudsters avg trust score: "+str(fraudsters_score_avg))
		return [honests_score_avg, fraudsters_score_avg]


	def store2Csv(self, file):
		dataset = h5py.File(self.dataset.dataset, 'a')
		trust_scores = dataset['trust_score'][:]
		with open(file, mode='w') as info:
			writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(["id", "trust_score", "status"])
			for i in range(self.scenario.n_providers,self.scenario.N):
				#trust_score = trust_scores[i][0]
				trust_score = trust_scores[i]
				status = 0
				if trust_score < self.manager.threshold:
					status = 1
				writer.writerow([i,trust_score, status])

	def storeRes(self, ):
		dataset = h5py.File(self.dataset.dataset, 'a')
		trust_scores = dataset['trust_score'][:]
		with open(file, mode='w') as info:
			writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(["id", "trust_score", "status"])
			for i in range(self.scenario.n_providers,self.scenario.N):
				#trust_score = trust_scores[i][0]
				trust_score = trust_scores[i]
				status = 0
				if trust_score < self.manager.threshold:
					status = 1
				writer.writerow([i,trust_score, status])
			