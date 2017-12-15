import h5py
import numpy as np
import numpy.linalg
import matplotlib.pyplot as plt

df = h5py.File("orthogonality_15123.hdf5", "r")

stage_positions = df["stage position000"]['stage position00000']
camera_positions = df["camera position000"]['camera position00000']

n = len(stage_positions)

pixel_shifts = camera_positions[:, :2] - np.mean(camera_positions[:, :2], axis = 0)
location_shifts = stage_positions[:, :2] - np.mean(stage_positions[:, :2], axis = 0)

A, res, rank, s = np.linalg.lstsq(pixel_shifts, location_shifts)
#A is the least squares solution pixcel_shifts*A = location_shifts
#res is the sums of residuals location_shifts - pixcel_shifts*A
#rank is rank of matrix pixcel_shifts
#s is singular values of pixcel_shifts
print A

#unit vectors
x = np.array([1,0]) 
y = np.array([0,1])

#dot products of A with x and y unit vectors to find x and y components of A
A_x = np.dot(A, x)
A_y = np.dot(A, y)

#uses standard dot product formula to find angle between A_x and A_y
dp = np.dot(A_x,A_y)
cosa = dp/(np.linalg.norm(A_x)*np.linalg.norm(A_y))
a = np.arccos(cosa)
b=a*180/np.pi
print b

plt.figure()
plt.plot(location_shifts[:, 0], location_shifts[:, 1], '+')
estimated_positions = np.dot(pixel_shifts, A)
#dot product pixcel_shifts . A 
plt.plot(estimated_positions[:, 0], estimated_positions[:, 1], 'o')

plt.figure()
plt.plot(pixel_shifts[:,0], pixel_shifts[:,1], 'o')
plt.figure()
plt.plot(pixel_shifts[:,1])
plt.plot(pixel_shifts[:,0])

plt.show()
