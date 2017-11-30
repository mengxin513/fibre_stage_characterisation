
#import libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
from plot_tools import plot_tools

def allan_variance(data, dt, npoints):
    """Calculate the Allan variance of 1D data, as explained in the paper."""
    assert data.ndim == 1    
    datapoints = data.shape[0]
    blocksizes = np.round(np.exp(np.linspace(0,1,npoints)*np.log(datapoints/4))).astype(np.int) #logarithmically seperates
    allan_var = np.empty((2,npoints))

    tau = blocksizes * dt
    
    for i, b in enumerate(blocksizes):
        data_blocked = data[0:(datapoints//b)*b].reshape((-1, b))
        xis = np.mean(data_blocked, axis=1)
        allan_var[0,i] = tau[i]
        allan_var[1,i] = 0.5 * np.mean(np.diff(xis, 1)**2)
    return allan_var

print "Loading data..." #indication of the programme running
df = h5py.File("drift.hdf5", "r") #reads data from file
group = df["test_data000"] #loads a data group

n = len(group) #finds the number of elements in the group
data = np.zeros([3, n*100]) #creates an empty array of zeros


for i in range(n):
    dset = group["data%05d" % i] #loads each dataset from the group
    data[:,i*100:(i*100+100)] = dset
    
filtered_data = data#[:,10000:40000]

dt = np.mean(np.diff(filtered_data[0,:]))

allan_x = allan_variance(filtered_data[1,:], dt, 200)
allan_y = allan_variance(filtered_data[2,:], dt, 200)
	
plot_data = np.zeros([3,allan_x.shape[1]])
plot_data[0:2, :] = allan_x 
plot_data[2, :] = allan_y[1,:]

plot_tools(plot_data)
plot_tools(data)
plt.show()