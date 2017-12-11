
#import libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
from plot_tools import plot_tools

print "Loading data..." #indication of the programme running
df = h5py.File("drift_41217.hdf5", "r") #reads data from file
group = df["test_data000"] #loads a data group

n = len(group) #finds the number of elements in the group
data = np.zeros([3, n]) #creates an empty array of zeros
for i in range(n):
    dset = group["data%05d" % i] #loads each dataset from the group
    data[:, i] = np.mean(dset, axis = 1) #finds the mean of each column in the dataset

plot_tools(data) #plots the graph
plt.show() #shows the plot on screen
