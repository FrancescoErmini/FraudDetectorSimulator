import numpy as np
import h5py
import logging

   
class EigenTrust():



	def __init__(self, scenario):
		super(EigenTrust, self).__init__()
		self.scenario = scenario
		




	def computeTrust(self, infile, outfile):

		logging.basicConfig(filename=outfile,level=logging.DEBUG)

		iterMax = 8

		preTrust_strategy = False

		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		n_pretrust = self.scenario.n_providers*self.scenario.provider_participation//100 + self.scenario.n_intermidiaries*self.scenario.intermidiaries_participation//100

		
		print("Create preTrust array")

		preTrust = np.empty(N)

		if N==n_pretrust or not preTrust_strategy:
			preTrust.fill((1.0/N))
		
		else:
			for i in range(N):
				if self.isPreTrust(i):
					preTrust[i] = 1.0/n_pretrust
				else:
					preTrust[i] = 0.0

		print("Create normalized matrix")

		dataset = h5py.File(infile, 'a')
		
		for j in range(N):

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset['fback_matrix'][::,j:j+1]
			#print("DEBUG")
			#print(fback_matrix_chunk)
			#calcolo la somma delle differenze (pos-neg) lungo la colonna j
			
			normalizer = 0

			for i in range(N):

				v = fback_matrix_chunk[i][0][0] - fback_matrix_chunk[i][0][1]
				#print("DEBUG")
				#print(v)
				if v < 0:
					v = 0.0
				normalizer += v
			#print(normalizer)

			#calcolo la colonna j della matrice normalizzata su un vettore d'appoggio tmp
			tmp = np.zeros(N)
			for i in range(N):
				fbackint = fback_matrix_chunk[i][0][0] - fback_matrix_chunk[i][0][1]
				if fbackint < 0:
					fbackint = 0
				if normalizer == 0.0:
					tmp[i] =  preTrust[i]
				else:
					tmp[i] = fbackint / normalizer
			#riporto il vettore tmp sulla colonna j della matrice normalizzata 
			dataset['normal_matrix'][::,j:j+1] = np.expand_dims(tmp,1)	
		#print((dataset['normal_matrix'][:]).tolist())
		


		print("Calcolo la reputazione")
		t = preTrust
		iteration = 0

		while iteration < iterMax:

			for i in range(N):
				#carico in memoria riga i della matrice normalizzata
				row = dataset['normal_matrix'][i:i+1,::][0]
				
				#moltiplico vettore colonna della matrice normalizzata con vettore t
				res=0
				for j in range(N):
					res+=(row[j]*t[j])
				#computo il trust secondo eigenTrust
				t[i] =  res
				#t[i] = 0.5 * res +  0.5 * preTrust[i]
		
				iteration += 1

		for i in range(N):
				logging.debug('USER: '+str(i)+' REP: '+str(t[i]))


				
		#print(t.tolist())


		good = 0
		bad = 0

		mean = np.mean(t)
		std = np.std(t)

		threshold = mean - std
		if threshold < 0:
			threshold = 0

		for i in range(self.scenario.n_providers, N):
			if t[i] <= threshold:
				bad += 1
			else:
				good += 1



		print("goolde")
		print(good)

		print("bad")
		print(bad)

		print("calc threshold:")
		print(threshold)

		
		'''
			for i in range(N):
				#carico in memoria riga i della matrice normalizzata
				row = dataset['normal_matrix'][i:i+1,::]
				#moltiplico vettore colonna della matrice normalizzata con vettore t
				t = np.dot(row,t)
				#computo il trust secondo eigenTrust
				t[i] = 0.5 * t[i] +  0.5 * preTrust[i]
				iteration += 1

		print(t)
		'''

	def isPreTrust(self, index):
		
		if index in range(0, self.scenario.n_providers*self.scenario.provider_participation//100):
			return True

		if index in range(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries*self.scenario.intermidiaries_participation//100) and not self.scenario.isFraudster(index):
			return True
		
		else:
			return False

	'''
	def calcMul(m_row, vect, N):
		res=0
		for j in range(N):
			res+=(m_row[j]*vect[j])
		return res
	'''
