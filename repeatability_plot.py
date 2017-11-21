
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
        mean_diff[:, j] = np.mean(diff, axis = 1) #takes the average of each column
        move[:, j] = moved_s[:] - init_s[:]
    abs_move = np.sqrt(np.sum(move**2, axis = 0)) #finds the average across a row
    error = np.sqrt(np.sum(mean_diff**2, axis = 0)) #averages all the differences in position after movement
    dist[:, i] = np.mean(abs_move, axis = 0) #stores the mean distace moved
    mean_error[:, i] = np.mean(error, axis = 0) #stores the mean error for each distance

    #plot the graphs for each move
    fig, ax = plt.subplots(1, 1)

    #r+ means plot using crosses
    ax.plot(mean_diff[0, :]*0.341, mean_diff[1, :]*0.341, 'r+')

    #set axis lables
    ax.set_xlabel('X [$\mathrm{\mu m}$]')
    ax.set_ylabel('Y [$\mathrm{\mu m}$]')

#plot the graph for the entire run
fig, ax2 = plt.subplots(1, 1)

#r- mean plot using a solid red line
ax2.plot(dist[0, :]*0.009, mean_error[0, :]*0.341, 'r-')

#set axis lables
ax2.set_xlabel('Move Distance [$\mathrm{\mu m}$]')
ax2.set_ylabel('Error [$\mathrm{\mu m}$]')

plt.show() #show plots on screen
