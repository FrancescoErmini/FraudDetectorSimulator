import numpy as np
import h5py
from config import Tools, TNSLAsettings
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
		#self.data = h5py.File(self.dataset.dataset, 'a')
		#self.prevtrust = np.zeros(self.scenario.n_intermidiaries)
		

	def initialize(self):
		pass
		'''
		dataset = h5py.File(self.dataset.dataset, 'a')

		for i in range(self.scenario.N):
			opinions = [[0.0, 0.0, 1.0, 0.5] for j in range(self.scenario.N)]
			data = dataset['opinion_matrix']
			data[:,i,:] = opinions
		'''


		
		#for i in range(self.scenario.n_providers):
			#pass
		#	self.pretrust[i] = 1.0
		

	"""
	A esprime le proprie opinoni sulla riga A
	B riceve le opinioni altrui sulla colonna B
	"""
		
	def computeTrust2(self, A, B):

		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		dataset = h5py.File(self.dataset.dataset, 'a')

		#print("Compue trust scores from feedback matrix with TNSLA")
		
		#carica pos e neg da A verso tutti, per evitare successivi acessi alla memoria
		fback_from_A =  dataset['fback_matrix_updated'][:]
		#print(fback_from_A)
		pos = fback_from_A[A][B][TNSLA.POS]
		neg = fback_from_A[A][B][TNSLA.NEG]

		#print("negAB "+str(neg))
		#print("posAB "+str(pos))

		if pos > 10 or neg > 10:
			#A has direct feedback over B, then compute directly A opion over B
			opinion_A_B = self.edit(pos, neg, self.pretrust[B])
			#store A opinion over B in the opinion matrix
			self.storeOpinion(A,B,opinion_A_B)
			print(str(A)+" has direct opinion over "+str(B))
			return self.eval(opinion_A_B)
		
		
		else:

			opinion_A_i = [0.0, 0.0, 1.0, 0.5]
			opinion_i_B = [0.0, 0.0, 1.0, 0.5]
			trustee_score = TNSLAsettings.trustee_score
			trustee_count = 0

			for i in range(self.scenario.N):
				pos_A_i = fback_from_A[A][i][TNSLA.POS]
				neg_A_i = fback_from_A[A][i][TNSLA.NEG]
				pos_i_B = fback_from_A[i][B][TNSLA.POS]
				neg_i_B = fback_from_A[i][B][TNSLA.NEG]

				
				if self.eval(self.edit(pos_A_i,neg_A_i, self.pretrust[i])) > trustee_score and self.eval(self.edit(pos_i_B,neg_i_B,self.pretrust[B]))!= 0.5:			

					#print("A "+str(A)+" best trustee for B "+str(B)+" is T "+str(i)+" with pretrust="+str(self.pretrust[i])+", posAi="+str(pos_A_i)+", negAi="+str(neg_A_i)+", posiB="+str(pos_i_B)+", negiB="+str(neg_i_B))
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
				#print("A "+str(A)+" don't have any trustee for B "+str(B))
				return 0.5
			else:
				#TNSLA.printOpinion(opinion_A_i)
				#TNSLA.printOpinion(opinion_i_B)
					
				opinion_A_B = self.discount(opinion_A_i, opinion_i_B)
				self.storeOpinion(A,B,opinion_A_B)
				res = self.eval(opinion_A_B)
				if res > 1.0 or res < 0.0:
					print("error occur")
					TNSLA.printOpinion(opinion_A_B)

				return res

	




	def computeTrust(self,target):
		
		#N = self.scenario.n_providers + self.scenario.n_intermidiaries
		
		if not self.scenario.isIntermidiary(target):
			#print("error: you can not compute. trust of an originating/terminating provider")
			return -1

		dataset = h5py.File(self.dataset.dataset, 'a')
		
		fback_to_target =  dataset['fback_matrix_updated'][:,target,:]

		opinion_all_target   = [0.0, 0.0, 1.0, 0.5]

		neg_counter = 0
		pos_counter = 0

		for j in range(self.scenario.N):
			
				pos_j_target = fback_to_target[j][TNSLA.POS]
				neg_j_target = fback_to_target[j][TNSLA.NEG]


				neg_counter += neg_j_target
				pos_counter += pos_j_target

				if pos_j_target > 0 or neg_j_target > 0:

					
						opinion_j_target = self.edit(pos_j_target, neg_j_target, self.pretrust[target])
						opinion_all_target = self.consensus(opinion_all_target, opinion_j_target)
		
		if neg_counter > 100 or pos_counter > 100:
			return self.eval(opinion_all_target)		
		else:
			return 0.5




				

		
	'''		
	def computeTrust3(self, A, B):

		N = self.scenario.n_providers + self.scenario.n_intermidiaries
		trustee_score = TNSLAsettings.trustee_score

		dataset = h5py.File(self.dataset.dataset, 'a')

		#print("Compue trust scores from feedback matrix with TNSLA")
		
		# - 1 - calcolo e salvo tutte le opinioni di A.
		fback_from_A =  dataset['fback_matrix_updated'][:]
		#for x in fback_from_A[:,0]:
		#	if x > 0:
		#			print("hey")
		trustee_count = 0


		opinion_A_T_B = [0.0, 0.0, 1.0, 0.5]
		opinion_A_T   = [0.0, 0.0, 1.0, 0.5]
		opinion_T_B   = [0.0, 0.0, 1.0, 0.5]
		found = False

		for i in range(self.scenario.N):
			# limitatamente ai nodi di interesse
			if self.scenario.isIntermidiary(i):	
			
				pos_A_i = fback_from_A[A][i][TNSLA.POS]
				neg_A_i = fback_from_A[A][i][TNSLA.NEG]
				#if pos_A_i != 0 and neg_A_i != 0:
				opinion_A_i = self.edit(pos_A_i, neg_A_i, self.pretrust[i])
				self.storeOpinion(A,i,opinion_A_i)

				# - 2 A - se A ha opinione diretta su B, calcola reputazione e termina.
				if i==B and (pos_A_i > 10 or neg_A_i > 10):
					print("A "+str(A)+" has direct opinion over "+str(B))
					return self.eval(opinion_A_i)

				# - 2 B - se A si fida di i, valuta la reputazione indiretta di i verso B e salvala
				if self.eval(opinion_A_i) > trustee_score:
					#TNSLA.printOpinion(opinion_A_i)
					
					#fback_from_i_to_B =  dataset['fback_matrix_updated'][B,i,:]
					#pos_i_B = fback_from_i_to_B[TNSLA.POS]
					#neg_i_B = fback_from_i_to_B[TNSLA.NEG]
					pos_i_B = fback_from_A[i][B][TNSLA.POS]
					neg_i_B = fback_from_A[i][B][TNSLA.NEG]

					# l'opinione di i verso B può essere presente anche se non ci sono feedback diretti, 
					# ad esempio nel caso in cui B abbia precedentemente chiesto l'opinione di i e l'ha ottenuta indirettamente.
					#if pos_i_B < 10 or neg_i_B < 10:
					#	opinion_i_B = self.getOpinion(i,B)
					#	if self.eval(opinion_i_B) != 0.5:
					#		found = True	
					
					if pos_i_B > 10 or neg_i_B > 10:
						opinion_i_B = self.edit(pos_i_B, neg_i_B, self.pretrust[B])
						self.storeOpinion(i,B,opinion_i_B)
						found = True
					else:
						found = False


					if found == True:
						if trustee_count == 0:
							opinion_A_T = opinion_A_i
							opinion_T_B = opinion_i_B
						else:
							opinion_A_T = self.consensus(opinion_A_T, opinion_A_i)
							opinion_T_B = self.consensus(opinion_T_B, opinion_i_B)
							
							#opinion_A_T_B = self.consensus(opinion_A_T_B, new_opinion_A_T_B)
						trustee_count+=1
		#endfor
		if found:
			opinion_A_T_B = self.discount(opinion_A_T, opinion_T_B)
			TNSLA.printOpinion(opinion_A_T)
			TNSLA.printOpinion(opinion_T_B)
					
			self.storeOpinion(A,B,opinion_A_T_B)
			res = self.eval(opinion_A_T_B)
			#debug purpose in case of overflow 
			if res > 1.0 or res < 0.0:
				TNSLA.printOpinion(opinion_A_B)
			return res			
		else:
			print("A "+str(A)+" don't have any trustee for B "+str(B))
			return 0.5
	'''


	def storeOpinion(self, _from, _to, opinion):
		#dataset_path = self.directory+'/'+str(self.cycle)+'/dataset.hdf5'
		dataset = h5py.File(self.dataset.dataset, 'a')
		dataset['opinion_matrix'][_to,_from,:] = opinion
		#data[_to,_from,:] = opinion

	def getOpinion(self, _from, _to):
		dataset = h5py.File(self.dataset.dataset, 'r')
		return dataset['opinion_matrix'][_to,_from,:]


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
		if denom == 0.0 or denom < 0.1:

			opinion_res[TNSLA.b] = (b1 + b2) / 2.0
			opinion_res[TNSLA.d] = 1.0 - opinion_res[TNSLA.b]
			opinion_res[TNSLA.u] = 0.0
		else:
			
			opinion_res[TNSLA.b] = 	(b1*u2 + b2*u1) / denom
			opinion_res[TNSLA.d] =  (d1*u2 + d2*u1) / denom
			opinion_res[TNSLA.u] =  (u1 * u2) / denom
			

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

		opinion_res[TNSLA.b] = b1 * b2
		opinion_res[TNSLA.d] = b1 * d2
		opinion_res[TNSLA.u] = d1 + u1 + b1*u2
		#opinion_res[TNSLA.u] = (1.0 - opinion_res[TNSLA.b]- opinion_res[TNSLA.d]);
		#double uncertainty = this.d + this.u + (this.b * that.u);
		opinion_res[TNSLA.a] = a2
		return opinion_res


	def printOpinion(opinion):
		print("belief: "+str(opinion[TNSLA.b]))
		print("disbelief: "+str(opinion[TNSLA.d]))
		print("uncertainty: "+str(opinion[TNSLA.u]))
		print("baserate: "+str(opinion[TNSLA.a]))
		

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
		
	
