import numpy as np
import h5py
from config import Tools
import csv
import pandas as pd
import random

   
class TNSLA():

	b = 0
	d = 1
	u = 2
	a = 3

	POS = 0
	NEG = 1



	def __init__(self, scenario, dataset):
		super(TNSLA, self).__init__()
		self.scenario = scenario
		self.dataset = dataset
		#self.cycle = cycle
		self.pretrust = [0.5 for i in range(self.scenario.N)]
		
		#self.prevtrust = np.zeros(self.scenario.n_intermidiaries)
		

	def initialize(self):
		for i in range(self.scenario.n_providers):
			#pass
			self.pretrust[i] = 1.0
		

		
		
	def computeTrust2(self, A, B):

		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		dataset = h5py.File(self.dataset.dataset, 'a')

		print("Compue trust scores from feedback matrix with TNSLA")
		
		#carica pos e neg da A verso tutti, per evitare successivi acessi alla memoria
		fback_from_A =  dataset['fback_matrix'][:]
		#print(fback_from_A)
		pos = fback_from_A[A][B][TNSLA.POS]
		neg = fback_from_A[A][B][TNSLA.NEG]

		print("negAB "+str(neg))
		print("posAB "+str(pos))

		if pos > 10 or neg > 10:
			#A has direct feedback over B, then compute directly A opion over B
			opinion_A_B = self.edit(pos, neg, self.pretrust[B])
			#store A opinion over B in the opinion matrix
			self.storeOpinion(A,B,opinion_A_B)
			print("stop")
			return self.eval(opinion_A_B)
		
		
		else:

			opinion_A_i  = np.zeros(4)
			opinion_i_B = np.zeros(4)
			trustee_score = 0.8
			trustee_count = 0

			for i in range(self.scenario.N):
				pos_A_i = fback_from_A[A][i][TNSLA.POS]
				neg_A_i = fback_from_A[A][i][TNSLA.NEG]
				pos_i_B = fback_from_A[i][B][TNSLA.POS]
				neg_i_B = fback_from_A[i][B][TNSLA.NEG]

				
				if self.eval(self.edit(pos_A_i,neg_A_i, self.pretrust[i])) > trustee_score and self.eval(self.edit(pos_i_B,neg_i_B,self.pretrust[B]))!= 0.5:			
					print("posAi "+str(pos_A_i))
					print("negAi "+str(neg_A_i))
					print("posiB "+str(pos_i_B))
					print("negiB "+str(neg_i_B))
					print("A best trustee is T: "+str(i))
					if trustee_count == 0:
						#update new trustee values
						opinion_A_i = self.edit(pos_A_i,neg_A_i,self.pretrust[i])
						opinion_i_B = self.edit(pos_i_B,neg_i_B, self.pretrust[B])
					else:
						opinion_A_i = self.consensus(opinion_A_i, self.edit(pos_A_i,neg_A_i, self.pretrust[i]))
						opinion_i_B = self.consensus(opinion_i_B, self.edit(pos_i_B,neg_i_B, self.pretrust[B]))
						#opinion_A_i = self.edit(pos_A_i,neg_A_i, self.pretrust[i])
						#opinion_i_B = self.edit(pos_i_B,neg_i_B, self.pretrust[B])
					#trustee_score = self.eval(opinion_A_i)
					trustee_count += 1



						#fback_from_T =  dataset['fback_matrix'][::,T:T+1]
			if trustee_count == 0:
				return -1
			else:
				opinion_A_B = self.discount(opinion_A_i, opinion_i_B)
				self.storeOpinion(A,B,opinion_A_B)
				return self.eval(opinion_A_B)



	def storeOpinion(self, _from, _to, opinion):
		#dataset_path = self.directory+'/'+str(self.cycle)+'/dataset.hdf5'
		dataset = h5py.File(self.dataset.dataset, 'a')
		dataset['opinion_matrix'][_to:_to+1,_from:_from+1] = opinion



	def eval(self, opinion):
		return opinion[TNSLA.b]+(opinion[TNSLA.a]*opinion[TNSLA.u])

	def edit(self, pos, neg, pretrust):

		opinion_res = np.zeros(4)
		opinion_res[TNSLA.b] = pos / (pos + neg + 2.0)
		opinion_res[TNSLA.d] = neg / (pos + neg + 2.0)
		opinion_res[TNSLA.u] = 2.0 / (pos + neg + 2.0)
		opinion_res[TNSLA.a] = pretrust
		return opinion_res

	def consensus(self, opinion1, opinion2):
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

	def discount(self, opinion1, opinion2):
		opinion_res = np.zeros(4)

		b1 = opinion1[TNSLA.b]
		d1 = opinion1[TNSLA.d]
		u1 = opinion1[TNSLA.u]
		a1 = opinion1[TNSLA.a]

		b2 = opinion2[TNSLA.b]
		d2 = opinion2[TNSLA.d]
		u2 = opinion2[TNSLA.u]
		a2 = opinion2[TNSLA.a]	

		opinion_res[TNSLA.b] = b1 * b2;
		opinion_res[TNSLA.d] = b1 * d2;
		opinion_res[TNSLA.u] = (1.0 - opinion_res[TNSLA.b]- opinion_res[TNSLA.d]);
		#double uncertainty = this.d + this.u + (this.b * that.u);
		opinion_res[TNSLA.a] = a2;
		return opinion_res



	'''
	def store2Csv(self, file):
		dataset = h5py.File(self.dataset.dataset, 'a')
		trust_scores = dataset['trust_score'][:]
		with open(file, mode='w') as info:
			writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(["id", "trust_score", "status"])
			for i in range(self.scenario.n_providers,self.scenario.N):
				trust_score = trust_scores[i][0]
				status = 0
				if trust_score < self.manager.threshold:
					status = 1
				writer.writerow([i,trust_score, status])




	def computeTrust(self, data_in, data_out):

		
		N = self.scenario.n_providers + self.scenario.n_intermidiaries

		dataset = h5py.File(self.dataset.dataset, 'a')

		trust = np.zeros((N,4))

		print("Compue trust scores from feedback matrix with TNSLA")
		
		for j in range(N):

			Tools.printProgress( j, N)

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset[data_in][::,j:j+1]
			pretrust = self.pretrust[j]
			tmp = np.zeros((N,4))
			
			for i in range(N):

				pos = fback_matrix_chunk[i][0][0]
				neg = fback_matrix_chunk[i][0][1]

				tmp[i] = self.edit(pos, neg, pretrust)

			op=tmp[0]
			
			for k in range(N-1):
				op = self.aggregate(op, tmp[k+1])
			trust[j] = op

			trustValue = trust[j][TNSLA.b]+(trust[j][TNSLA.a]*trust[j][TNSLA.u])
			dataset[data_out][j] = trustValue
	'''
		
	
