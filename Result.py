class Result:

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

