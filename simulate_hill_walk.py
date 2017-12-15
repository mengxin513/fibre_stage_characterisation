import numpy as np
import matplotlib.pyplot as plt
import time
import math

pos = np.array([0,0,0],dtype=np.float)
maxpos = np.array([3984.6, 4832., 12048.])

def take_data(stage, points, samples, step_size, axis):
    global pos
    time.sleep(1)
    data = np.zeros((points, 5), dtype=np.float)
    pos += (np.dot(-(step_size * math.trunc(points / 2)), axis))
    for i in range(points):
        pos += (np.dot(step_size, axis))
        data[i, 0] = np.exp(-np.sum((pos - maxpos)**2/np.array([1000.,1000.,3000.])**2))*1000.
        data[i, 1] = 1
        data[i, 2:] = pos
    return data


if __name__ == "__main__":
    plt.ion()
    fig, axes = plt.subplots(1,2)
    intensity_data = np.empty((100, 5))
    intensity_data[:,:] = np.nan
    n = 0
    points = 5
    for step_size in [500, 100]:
        for axis in [[1,0,0],[0,1,0],[0,0,10]]:
            axis = np.array(axis)
            while True:
                data = take_data(None, points, 5, step_size, axis)
                print data
                x = np.dot(data[:, 2:], axis)
                intensity = data[:,0]
                coefficients = np.polyfit(x, intensity, 2)
                axes[1].cla()
                axes[1].plot(x, intensity, 'o-')
                axes[1].plot(x, coefficients[0]*x**2 + coefficients[1]*x + coefficients[0])
                fig.canvas.draw()
                gradients = np.zeros((points, 1))
                gradients[:, 0] = (2 * coefficients[0] * x) + coefficients[1]
                signs_sum = np.sum(np.sign(gradients[:, 0]))
                intensity_data[n,:] = np.mean(data,axis=0)
                n+=1
                axes[0].cla()
                ss = np.log(intensity_data[:,0])
                axes[0].scatter(intensity_data[:,2], intensity_data[:,3], s=ss/np.nanmean(ss)*100)
                fig.canvas.draw()
                if 
                elif signs_sum == points:
                    print "Not at the peak yet, working hard on it"
                    pos = (data[points-1, 2:])
                    continue
                elif signs_sum == -points:
                    print "Getting bored? I'm nearly there"
                    pos = (data[0, 2:])
                    continue
                else:
                    print "Look I just found the peak"
                    pos_to_be = -(coefficients[1] / (2 * coefficients[0]))
                    axes[1].axvline(pos_to_be)
                    fig.canvas.draw()
                    pos += (np.dot((pos_to_be - np.dot(data[points-1, 2:], axis)), axis)/np.sum(axis**2))
                    break
    plt.show()
