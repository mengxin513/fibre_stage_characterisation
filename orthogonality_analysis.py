
import h5py
import numpy as np
import numpy.linalg
import matplotlib.pyplot as plt

df = h5py.File("orthogonality.hdf5", "r")

stage_positions = df["stage position"]
camera_positions = df["camera position"]

pixel_shifts = camera_positions[:, :2] - np.mean(camera_position[:, :2], axis = 0)
location_shifts = stage_position[:, :2] - np.mean(stage_positions[:, :2], axis = 0)

A, res, rank, s = np.linalg.lstsq(pixel_shifts, location_shifts)
#A is the least squares solution pixcel_shifts*A = location_shifts
#res is the sums of residuals location_shifts - pixcel_shifts*A
#rank is rank of matrix pixcel_shifts
#s is singular values of pixcel_shifts

#unit vectors
x = np.array([1,0]) 
y = np.array([0,1])

#dot products of A with x and y unit vectors to find x and y components of A
A_x = A*x
A_y = A*y

#uses standard dot product formula to find angle between A_x and A_y
dp = A_x*A_y
cosa = dp/(np.linalg.norm(A_x)*np.linalg.norm(A_y))
a = np.arccos(cosa)

plt.figure()
plt.plot(location_shifts[:, 0], location_shifts[:, 1], '+')
estimated_positions = np.dot(pixcel_shifts, A)
#dot product pixcel_shifts . A 
plt.plot(estimated_positions[:, 0], estimated_positions[:, 1], 'o')
plt.gca.set_aspect(1)


