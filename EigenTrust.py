import numpy as np
import h5py
import logging

   
class EigenTrust():

	n_providers = 0
	n_intermidiaries = 0
	provider_participation = 0
	intermidiaries_participation = 0

	def __init__(self, n_providers, n_intermidiaries, provider_participation, intermidiaries_participation):
		super(EigenTrust, self).__init__()
		self.n_providers = n_providers
		self.n_intermidiaries = n_intermidiaries
		self.provider_participation = provider_participation
		self.intermidiaries_participation = intermidiaries_participation




	def computeTrust(self, dataset_path):

		logging.basicConfig(filename=dataset_path+'/rawresult.log',level=logging.DEBUG)

		iterMax = 10

		booo = False

		N = self.n_providers + self.n_intermidiaries

		
		print("Create preTrust array")
		preTrust = np.empty(N) #[0 for i in range(N)]
		preTrust.fill((1.0/N))
		if booo:
			n_trust1 = self.n_providers*self.provider_participation//100
			n_trust2 = self.n_intermidiaries*self.intermidiaries_participation//100
			n_pretrust = int(n_trust1) + int(n_trust2)

			for i in range(N):
				if i < n_trust1 and n_pretrust<N:
					preTrust[i] = 1.0/n_pretrust
				if i < int(self.n_providers+n_trust2) and i > int(self.n_providers):
					preTrust[i] = 1.0/n_pretrust
				else:
					preTrust[i] = 0.0

		print(preTrust)
		#with h5py.File(dataset_path+"/dataset.hdf5", "a") as f:
			#f.create_dataset("fback_matrix", data=a)
			#f.create_dataset("normal_matrix", shape=(N,N))
		print("Create normalized matrix")

		dataset = h5py.File(dataset_path+'/dataset.hdf5', 'a')
		
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
				#t[i] =  res
				t[i] = 0.5 * res +  0.5 * preTrust[i]

				logging.debug('ITER: '+str(iteration)+' USER: '+str(i)+' REP: '+str(t[i]))
		
				iteration += 1

				
		#print(t.tolist())


		good = 0
		bad = 0

		mean = np.mean(t)
		std = np.std(t)

		threshold = mean - std
		if threshold < 0:
			threshold = 0

		for i in range(N):
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
	def calcMul(m_row, vect, N):
		res=0
		for j in range(N):
			res+=(m_row[j]*vect[j])
		return res
