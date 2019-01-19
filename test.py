import h5py
import numpy as np

# create an hdf5 file
#with h5py.File("matrix4.hdf5") as f:
 #M = f.create_dataset("mymatrix", shape=(10, 10, 2), dtype=np.uint8)
    # fill the 10 frames with a random image
#for frame in range(10):
#    dst[frame,frame,0] = np.random.randint(5)


# create an hdf5 file
f = h5py.File('m.hdf5', 'r')

dset = f[:,:,1]

print dset

#for frame in range(10):
#	print(dset[frame,frame,0])