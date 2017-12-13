
import h5py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

print("Loading data")
df = h5py.File("hillwalk.hdf5", "r")
n = len(df)

x = np.zeros((1, n))
y = np.zeros((1, n))
z = np.zeros((1, n))
area = np.zeros((1, n))

for i in range(n):
    dset = df["data%03d" %i]
    x[:] = dset[3, 3]
    y[:] = dset[3, 4]
    z[:] = dset[3, 5]
    area[:] = np.pi * (dset[3, 0] * dset[3, 1])**2
    colour[:] = dset[3, 2]

fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')

ax.scatter(x, y, z, zdir = 'z', s = area, marker = 'o', c = colour, cmap = cm.jet)

ax.set_xlabel('x position')
ax.set_ylabel('y position')
ax.set_zlabel('z position')
plt.title("Auto-alignment")
plt.colourbar(graph)
plt.show()
