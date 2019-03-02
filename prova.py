import numpy as np
import h5py
   
def main():

	N = 60

	#with h5py.File("matrix.hdf5", "a") as f:
	#	f.create_dataset("bigM", shape=(N,N, 2), dtype=np.uint8)

	fr = h5py.File('m.hdf5', 'r')
	matrix = fr['bigM'][:][0][:]

	print(matrix)

	print 






if __name__ == '__main__':
   main()