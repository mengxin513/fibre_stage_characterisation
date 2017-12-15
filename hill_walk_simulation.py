
#from openflexure_stage import OpenFlexureStage
import numpy as np
import math
import time
import h5py
import data_file
from contextlib import closing


pos = np.array([0,0,0],dtype=np.float)
maxpos = np.array([3984.6, 4832., 12048.])
stage = None

def take_data(stage, points, samples, step_size, axis, start_time):
    global pos
    time.sleep(0.01)
    data = np.zeros((points, 6), dtype=np.float)
    pos += (np.dot(-(step_size * math.trunc(points / 2)), axis))
    for i in range(points):
        pos += (np.dot(step_size, axis))
        data[i, 0] = np.exp(-np.sum((pos - maxpos)**2/np.array([1000.,1000.,3000.])**2))*1000.
        data[i, 1] = 1
        data[i, 2] = time.time() - start_time
        data[i, 3:] = pos
    return data

if __name__ == "__main__":
    with closing(data_file.Datafile(filename = "hillwalk.hdf5")) as df:

        gain = [1, 25, 428, 9876]
        #stage.light_sensor_gain = 9876
        step_size = 500
        min_step = 50
        points = 5
        samples = 5

#        stage.backlash = 256

        raw_data = df.new_group("data", "hill walk")

        start_time = time.time()

        while step_size > min_step:
            for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 10]]:
                while True:
                    data = take_data(stage, points, samples, step_size, axis, start_time)
                    print data
                    df.add_data(data, raw_data, "data")
                    #if np.all(data[:, 0] < 10) == True:
                    #    current_gain = stage.light_sensor_gain
                    #    if current_gain < np.max(gain):
                    #        stage.light_sensor_gain = np.min([g for g in gain if g > current_gain])
                    #        continue
                    #elif np.all(data[:, 0] > 2**15) == True:
                    #    current_gain = stage.light_sensor_gain
                    #    if current_gain > np.min(gain):
                    #        stage.light_sensor_gain = np.max([g for g in gain if g < current_gain])
                    #        continue
                    coefficients = np.polyfit(np.dot(data[:, 3:], axis), data[:, 0], 2)
                    if 2 * coefficients[0] > 0:
                        coefficient = np.polyfit(np.dot(data[:, 3:], axis), data[:, 0], 1)
                        if coefficient[0] > 0:
                            print "straight line with positive gradient"
                            #stage.move_abs(data[points-1, 3:])
                            pos = data[points-1, 3:]
                            continue
                        elif coefficient[0] < 0:
                            print "straight line with negative gradient"
                            #stage.move_abs(data[0, 3:])
                            pos = data[0, 3:]
                            continue
                    elif 2 * coefficients[0] < 0:
                        gradients = np.zeros((points, 1))
                        gradients[:, 0] = (2 * coefficients[0] * np.dot(data[:, 3:], axis)) + coefficients[1]
                        signs_sum = np.sum(np.sign(gradients[:, 0]))
                        if signs_sum == points:
                            print "Not at the peak yet, working hard on it"
                            #stage.move_abs(data[points-1, 3:])
                            pos = data[points-1, 3:]
                            continue
                        elif signs_sum == -points:
                            print "Getting bored? I'm nearly there"
                            #stage.move_abs(data[0, 3:])
                            pos = data[0, 3:]
                            continue
                        else:
                            print "Look I just found the peak"
                            pos_to_be = -(coefficients[1] / (2 * coefficients[0]))
                            #stage.move_rel(np.dot((pos_to_be - np.dot(data[points-1, 3:], axis)), axis)/np.sum(np.array(axis)**2))
                            pos += (np.dot((pos_to_be - np.dot(data[points-1, 3:], axis)), axis)/np.sum(np.array(axis)**2))
                            break
                
            step_size = np.rint(step_size / 2)
            print "Step size reduced to %d" %step_size
            
#        print stage.light_sensor_fullspectrum
#        print stage.light_sensor_gain
#        print stage.position
        