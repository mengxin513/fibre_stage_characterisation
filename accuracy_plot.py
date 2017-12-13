import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

print "Loading data..." #indication of the programme running
df = h5py.File("accuracy.hdf5", "r") #reads data from file
data = df['text_data000']['data00000']

matplotlib.rcParams.update({'font.size': 8})

#: means everything
t=data[0,:]
x=data[1,:]*0.341
y=data[2,:]*0.341

#plot the graph
fig, axes = plt.subplots(1,2)
        
#r- means solid red line
xt_plot, = axes[0].plot(t, x, 'r-')
ax2 = axes[0].twinx()
yt_plot, = ax2.plot(t, y, 'b-')
                
#second graph
axes[1].plot(x, y, 'r-')
axes[1].set_aspect(1)
        
#set axis lables
axes[0].set_xlabel('Time [$\mathrm{s}$]')
axes[0].set_ylabel('X [$\mathrm{\mu m}$]')
ax2.set_ylabel('Y [$\mathrm{\mu m}$]')
axes[1].set_xlabel('X [$\mathrm{\mu m}$]')
axes[1].set_ylabel('Y [$\mathrm{\mu m}$]')
        
#set legend
axes[0].legend([xt_plot, yt_plot], ['X', 'Y'], loc='upper left')
#ax2.legend('Y',loc='upper right')
		
plt.tight_layout() #prevents graph overlap
plt.show() #show plots
