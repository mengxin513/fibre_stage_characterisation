
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

plt.figure()
plt.plot(location_shifts[:, 0], location_shifts[:, 1], '+')
estimated_positions = np.dot(pixcel_shifts, A)
#dot product pixcel_shifts . A 
plt.plot(estimated_positions[:, 0], estimated_positions[:, 1], 'o')
plt.gca.set_aspect(1)