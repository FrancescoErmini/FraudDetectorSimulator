import numpy as np
import h5py
   
def main():

	big=True

	iterMax = 1

	#shape = (3, 3, 2)

	N = 100

	#a = np.array([ [ [0,0], [3,1] ,[3,2] ], [ [9,3], [0,0] ,[8,1] ], [ [2,4], [5,4] ,[0,0] ] ])
	a = np.random.randint(5, size=(N,N,2))

	normal =  np.zeros((N,N))



	p = np.full(N, 1.0/N)



	if big==True:

		with h5py.File("dataset.hdf5", "a") as f:
			f.create_dataset("fback_matrix", data=a)
			f.create_dataset("normal_matrix", shape=(N,N))
		dataset = h5py.File('dataset.hdf5', 'a')

		
		print("Normalizzo la matrice dei feedback")
		for j in range(N):

			#carico in memoria la colonna j della matrice dei feedback
			fback_matrix_chunk =  dataset['fback_matrix'][::,j:j+1]
			
			#calcolo la somma delle differenze (pos-neg) lungo la colonna j
			normalizer = 0
			for i in range(N):
				v = fback_matrix_chunk[i][0][0] - fback_matrix_chunk[i][0][1]
				#print(v)
				if v < 0:
					v = 0
				normalizer += v

			#calcolo la colonna j della matrice normalizzata su un vettore d'appoggio tmp
			tmp = np.zeros(N)
			for i in range(N):
				fbackint = fback_matrix_chunk[i][0][0] - fback_matrix_chunk[i][0][1]
				if fbackint < 0:
					fbackint = 0
				if normalizer == 0:
					tmp[i] = 1.0 / p[i]
				else:
					tmp[i] = fbackint / normalizer
			#riporto il vettore tmp sulla colonna j della matrice normalizzata 
			dataset['normal_matrix'][::,j:j+1]=np.expand_dims(tmp,1)	
		#print(dataset['normal_matrix'][:])
		


		print("Calcolo la reputazione")
		t = p
		iteration = 0 
		trust = np.zeros(N)

		while iteration < iterMax:

			for i in range(N):
				#carico in memoria riga i della matrice normalizzata
				row = dataset['normal_matrix'][i:i+1,::]
				#moltiplico vettore colonna della matrice normalizzata con vettore t
				trust[i] = np.dot(row,t)
				#computo il trust secondo eigenTrust
				trust[i] = 0.5 * trust[i] +  0.5 * p[i]
				iteration += 1

		
		print(trust)
		


	else:

		print("Normalizzo la matrice dei feedback")
		for j in range(N):
			normalizer = 0
			for i in range(N):
				v = (a[i,j,0] - a[i,j,1])
				if v < 0:
					v = 0.0
				normalizer += v

			for i in range(N):
				fbackint = a[i,j,0] - a[i,j,1]
				if fbackint < 0:
					fbackint = 0
				if normalizer == 0.0:
					normal[i,j] = p[i]
				else:
					normal[i,j] = fbackint / normalizer
		print(normal)
		print("Calcolo reputazione")
		t = p
		iteration = 0 
		while iteration < iterMax:
			t = np.dot(0.5, np.dot(normal,t)) + np.dot(0.5,p)  #0.16666666
			iteration += 1	
		print(t)
	

if __name__ == '__main__':
	main()