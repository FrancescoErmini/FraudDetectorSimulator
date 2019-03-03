import numpy as np
import h5py
import logging

   
class TNSLA():



	def __init__(self, scenario):
		super(TNSLA, self).__init__()
		self.scenario = scenario
		




	def computeTrust(self, infile, outfile):

		logging.basicConfig(filename=outfile,level=logging.DEBUG)

		
		N = self.scenario.n_providers + self.scenario.n_intermidiaries


		dataset = h5py.File(infile, 'a')
		
		for j in range(N):

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset['fback_matrix'][::,j:j+1]
			

			dataset['opinion_matrix'][::,j:j+1] = np.expand_dims(tmp,1)	
		
	
