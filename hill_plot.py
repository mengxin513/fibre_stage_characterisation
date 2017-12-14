
import h5py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

print("Loading data")
df = h5py.File("hillwalk.hdf5", "r")
group = df.values()[-1]

n = len(group)

x = np.zeros(n)
y = np.zeros(n)
z = np.zeros(n)
time = np.zeros(n)
area = np.zeros(n)

all_points = np.zeros((n*5, 4))

for i in range(n):
    dset = group["data%05d" %i]
    x[i] = dset[3, 3]
    y[i] = dset[3, 4]
    z[i] = dset[3, 5]
    time[i] = dset[3, 2]
    area[i] = np.log(dset[3, 0] / float(dset[3, 1]))
    all_points[(i*5):(i+1)*5, :3] = dset[:,3:]
    all_points[(i*5):(i+1)*5, 3] = dset[:,0]/dset[:,1].astype(np.float)

area -= np.min(area)
area /= np.max(area)
area *= np.pi * 50**2

alpha = area.copy()
alpha /= np.max(alpha)
    
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')

graph = ax.scatter(x, y, z, zdir = 'z', s = area, c = time, marker = 'o', cmap = cm.jet)

ax.set_xlabel('x position')
ax.set_ylabel('y position')
ax.set_zlabel('z position')
plt.title("Auto-alignment")
fig.colorbar(graph)

fig, axes = plt.subplots(1,3, sharey=True)

for i in range(n):
    dset = group["data%05d" %i]
    for j in range(3):
        axes[j].plot(dset[:,j+3], np.log(dset[:, 0] / dset[:, 1].astype(float)))

plt.show()
