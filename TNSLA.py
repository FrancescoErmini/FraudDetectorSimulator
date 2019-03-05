import numpy as np
import h5py
from config import Tools


   
class TNSLA():

	b = 0
	d = 1
	u = 2
	a = 3



	def __init__(self, scenario):
		super(TNSLA, self).__init__()
		self.scenario = scenario
		

	def computeTrust(self, data_in, data_out):

		
		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		dataset = h5py.File(self.scenario.dataset, 'a')

		trust = np.zeros((N,4))

		print("Compue trust scores from feedback matrix with TNSLA")
		
		for j in range(N):

			Tools.printProgress( j, N)

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset[data_in][::,j:j+1]
			
			tmp = np.zeros((N,4))
			
			for i in range(N):

				pos = fback_matrix_chunk[i][0][0]
				neg = fback_matrix_chunk[i][0][1]

				tmp[i] = self.edit(pos, neg)

			op=tmp[0]
			
			for k in range(N-1):
				op = self.aggregate(op, tmp[k+1])
			trust[j] = op

			trustValue = trust[j][TNSLA.b]+(trust[j][TNSLA.a]*trust[j][TNSLA.u])
			dataset[data_out][j] = trustValue


	def edit(self, pos, neg):

		opinion_res = np.zeros(4)
		opinion_res[TNSLA.b] = pos / (pos + neg + 2.0)
		opinion_res[TNSLA.d] = neg / (pos + neg + 2.0)
		opinion_res[TNSLA.u] = 2.0 / (pos + neg + 2.0)
		opinion_res[TNSLA.a] = 0.5
		return opinion_res

	def aggregate(self, opinion1, opinion2):
		opinion_res = np.zeros(4)

		b1 = opinion1[TNSLA.b]
		d1 = opinion1[TNSLA.d]
		u1 = opinion1[TNSLA.u]
		a1 = opinion1[TNSLA.a]

		b2 = opinion2[TNSLA.b]
		d2 = opinion2[TNSLA.d]
		u2 = opinion2[TNSLA.u]
		a2 = opinion2[TNSLA.a]		

		denom = u1 + u2 - u1 * u2
		if denom != 0:
			
			opinion_res[TNSLA.b] = 	(b1*u2 + b2*u1) / denom
			opinion_res[TNSLA.d] =  (d1*u2 + d2*u1) / denom
			opinion_res[TNSLA.u] =  (u1 * u2) / denom
		else:
			opinion_res[TNSLA.b] = (b1 + b2) / 2.0
			opinion_res[TNSLA.d] = 1.0 - opinion_res[TNSLA.b]
			opinion_res[TNSLA.u] = 0.0

		opinion_res[TNSLA.a] = a1

		return opinion_res





		
	