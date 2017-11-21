import h5py
import numpy as np
import np.linalg
import matplotlib.pyplot as plt

df = h5py.File("orthogonality_test.h5", "r")

group = df["test_orthogonality_measurement"]
stage_positions = []
camera_positions = []
for m in group.values():
    stage_positions.append(m['stage_position'])
    camera_positions.append(np.mean(m['camera_position'], axis=0))
stage_positions = np.array(stage_positions)
camera_positions = np.array(camera_positions)

pixel_shifts = camera_positions[:,:2] - np.mean(camera_positions[:,:2], axis=0)
location_shifts = stage_positions[:,:2] - np.mean(stage_positions[:,:2], axis=0)

A, res, rank, s = np.linalg.lstsq(pixel_shifts, location_shifts) # we solve pixel_shifts*A = location_shifts

plt.figure()
plt.plot(location_shifts[:,0], location_shifts[:,1], "+")
estimated_positions = np.dot(pixel_shifts,A)
plt.plot(estimated_positions[:,0], estimated_positions[:,1], 'o')
plt.gca().set_aspect(1)
