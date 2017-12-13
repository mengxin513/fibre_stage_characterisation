import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

print "Loading data..." #indication of the programme running
df = h5py.File("step_size.hdf5", "r") #reads data from file
data = df['step_size000']['data00000']

matplotlib.rcParams.update({'font.size': 8})

fig, ax = plt.subplots(1,1)

ax.plot(data[0, :], data[1, :], 'r-')
	
ax.set_xlabel('number of steps')
ax.set_ylabel('step_size [$\mathrm{\mu m}$]')
    
plt.title("Step Size Measurment")

plt.show() #show plots