import h5py
import numpy as np


df = h5py.File("orthogonality_test.h5")

s = 5000/2
n_measurements = 0
points_per_side = 10
random_error = 1

corners = np.array([[-s,-s,0], [s,-s,0], [s,s,0], [-s,s,0], [-s,-s,0]])
for i in range(corners.shape[0] - 1):
    for a in np.linspace(0,1,points_per_side):
        pos = corners[i]*(1-a) + corners[i+1]*a
        df["test_orthogonality_measurement/point_%03d/stage_position" % n_measurements] = pos
        df["test_orthogonality_measurement/point_%03d/camera_position" % n_measurements] = np.array([pos[0]+pos[1], pos[0]-pos[1], pos[2]])[np.newaxis,:]*0.24 + (np.random.rand(10,3) - 0.5)*random_error
        n_measurements += 1
df.close()
        