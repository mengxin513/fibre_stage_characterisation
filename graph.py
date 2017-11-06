
#import libraries
import cv2
import numpy as np
from scipy import ndimage, signal
import matplotlib.pyplot as plt
import matplotlib
import data_file
import h5py

matplotlib.rcParams.update({'font.size': 8})

print "Loading data..." #indication of the programme running
datafile=h5py.File("positions.hdf5", "r") #read in data
group = datafile["test_data000"]
data = np.array(group.values()[0])
datafile.close()

#: means everything
t=data[0,:]
x=data[1,:]
y=data[2,:]

#plot the graph
fig = plt.figure(figsize=(3.37,3),dpi=180)
ax = fig.add_subplot(1, 1, 1)

#r- means solid red line
for v, fmt in zip([x, y], ['r+','b+']):
    ax.plot(t, v, fmt, linewidth=3)

#set axis lables
ax.set_xlabel('Time [$\mathrm{s}$]')
ax.set_ylabel('Position [$\mathrm{\mu m}$]')

#set legend
ax.legend( ('X', 'Y'), loc='upper left')

#save the graph
fig.tight_layout()
for fmt in ['pdf','png','eps']:
    fig.savefig('drift.'+fmt, bbox_inches='tight', dpi=180)
plt.close(fig)
