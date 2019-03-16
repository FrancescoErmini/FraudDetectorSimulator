class TrustManager(object):

	def __init__(self, scenario, dataset):
		super(TrustManager, self).__init__()

		self.scenario = scenario
		self.dataset = dataset

		self.fraudsters_detection = 0
		self.fraudsters_detection_suspect = 0
		self.fraudsters_detection_error = 0
		self.fraudsters_detection_missing = 0

		self.honests_detection = 0
		self.honests_detection_suspect = 0
		self.honests_detection_error  = 0
		self.honests_detection_missing = 0

		self.threshold = 0


	def fraudsterClassifier(self, data_in, outfile):



		dataset = h5py.File(self.dataset.dataset, 'r')
		trust_scores = dataset['trust_score'][self.scenario.n_providers:self.scenario.N,0]

		avg = np.mean(trust_scores)
		std = np.std(trust_scores)

		self.threshold = avg - std

		if self.threshold < 0.5:
			self.threshold = 0.5

		print("\nClassifying peers into fraudsters and honests using trust scores.")
		for i in range(self.scenario.n_intermidiaries):
		
			if self.scenario.isFraudster(i+self.scenario.n_providers):
				if trust_scores[i] < 0.5:
					#print("fraudster is: " + str(i+self.scenario.n_providers) + " with score values: " +  str(Tscore[i]) +"<"+str(self.threshold))
					self.fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < 0.9 and trust_scores[i] < self.threshold:

					self.suspected_fraudsters += 1

				if trust_scores[i] > 0.5 and trust_scores[i] < 0.9 and trust_scores[i] > self.threshold:
					
					self.suspected_falsenegative += 1

				if trust_scores[i] >= 0.9:

					self.falsenegative += 1

				if trust_scores[i] == 0.5:

					self.unknown_fraudsters += 1
			else:

				if trust_scores[i] >= 0.9:

					self.honests += 1

				if trust_scores[i] < 0.9 and trust_scores[i] > 0.5 and trust_scores[i] > self.threshold:
					
					self.suspected_honests += 1

				if trust_scores[i] < 0.9 and trust_scores[i] > 0.5 and trust_scores[i] < self.threshold:

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
