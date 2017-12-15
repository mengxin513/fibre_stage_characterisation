import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.mlab as mlab
import data_file

print "Loading data..." #indication of the programme running
df = h5py.File("background.hdf5", "r") #reads data from file
data = df['data000']
n = len(data)
n_bins = 50
gain = [1,25,428,9876]
for i in range(n):
    gain_gr = data['Gain%03d' % i]
    x = gain_gr['data00000']
    mean = np.mean(x)
    sd = np.std(x)
    fig, ax = plt.subplots(1,1)
    j, bins, patches = ax.hist(x, n_bins, normed=1)
    y = mlab.normpdf(bins, mean, sd)
    ax.plot(bins, y, '--')
    ax.set_xlabel('Intensity')
    ax.set_ylabel('Probability density')
    ax.set_title(r'Histogram of Background noise: gain=%d, $\mu=%d$, $\sigma=%d$' % (gain[i],mean, sd))

plt.show()
    
    
