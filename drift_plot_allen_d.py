
#import libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
from plot_tools import plot_tools

def allan_variance(data, dt, npoints):
    """Calculate the Allan variance of 1D data, as explained in the paper."""
    assert data.ndim == 1    
    datapoints = data.shape[0]
    blocksizes = np.round(np.exp(np.linspace(0,1,npoints)*np.log(datapoints/4))).astype(np.int)
    allan_var = np.empty((npoints,2))

    tau = blocksizes * dt
    for i, b in enumerate(blocksizes):
        data_blocked = data[0:np.floor(datapoints/b)*b].reshape((-1, b))
        xis = np.mean(data_blocked, axis=1)
        allan_var[0,i] = tau[i]
        allan_var[1,i] = 0.5 * np.mean(np.diff(xis, 1)**2)
    return allan_var

print "Loading data..." #indication of the programme running
df = h5py.File("drift.hdf5", "r") #reads data from file
group = df["test_data000"] #loads a data group

n = len(group) #finds the number of elements in the group
data = np.zeros([3, n]) #creates an empty array of zeros

for i in range(n):
    dset = group["data%05d" % i] #loads each dataset from the group
    data[:, i] = np.mean(dset, axis = 1) #finds the mean of each column in the dataset

data[1,:] *= 0.341 #turns pixels to um
data[2,:] *= 0.341 #turns pixeks to um

dt = 100

allen_x = np.zeros(2,npoints)
allen_y = np.zeros(2,npoints)
allens_x = allan_variance(data[1,:], dt, n)
allens_y = allan_variance(data[2,:], dt, n)
	
plot_tools(allen_x) #plots the graph

plot_tools(allen_y) #plots the graph