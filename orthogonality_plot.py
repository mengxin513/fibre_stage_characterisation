#import libraries
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from scipy import ndimage, signal
import data_file

print "Loading data..." #indication of the programme running
df = h5py.File("orthogonality.hdf5", "r") #reads data from file
group = df["Orthogonality"] 

for i in [1,10,25]:

    dset = group["step_%d" % i]

    #plot the graphs for each move
    fig, ax = plt.subplots(1, 1)

    #r+ means plot using crosses
    ax.plot(dset[0,:]*0.341, dset[1,:]*0.341, 'r+')

    #set axis lables
    ax.set_xlabel('X [$\mathrm{\mu m}$]')
    ax.set_ylabel('Y [$\mathrm{\mu m}$]')
