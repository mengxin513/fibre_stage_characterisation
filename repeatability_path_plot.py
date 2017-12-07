
#import libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from scipy import ndimage, signal
import data_file

print "Loading data..." #indication of the programme running
df = h5py.File("repeat.hdf5", "r") #reads data from file
n = len(df) #finds the number of items in the file
dist = np.zeros([1, n]) #creates array of zeros
mean_error = np.zeros([1, n])
for i in range(n):   
    fig, ax = plt.subplots(1, 1) #plot the graphs for each move
    group = df["repeatability%03d" % i] #loads data groups
    m = len(group)
    mean_diff = np.zeros([2,m])
    move = np.zeros([3, m])
    for j in range(m):
        dset = group["move%03d" % j] #loads datasets
        init_c = dset["init_cam_position"]
        final_c = dset["final_cam_position"]
        init_s = dset["init_stage_position"]
        moved_s = dset["moved_stage_position"]
        p = len(init_c)
        diff = np.zeros([2, p])
        for k in range(p):
            diff[:, k] = final_c[1:, k] - init_c[1:, k] #1: excludes the 0th element
            ax.plot(init_c[1:,k]*0.341, final_c[1:,k]*0.341, marker='+', linestyle = '-')

plt.show() #show plots on screen
