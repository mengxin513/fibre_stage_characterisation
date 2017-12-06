
from openflexure_stage import OpenFlexureStage
import numpy as np
import h5py
import time
import math
import data_file

def take_data(stage, points, samples, direction, step_size, axis):
    data = np.zeros((points, 5))
    avg = np.zeros((samples, 1))
    stage.move_rel(np.dot(math.trunc(-(step_size * points / 2)), axis))
    for i in range(points):
        for j in range(samples):
            avg[j, 0] = stage.light_sensor_fullspectrum
            time.sleep(0.1)
        data[i, 0] = np.mean(avg, axis = 0)
        data[i, 1] = stage.light_sensor_gain
        data[i, 2:] = stage.position
    return data

if __name__ == "__main__":
    with OpenFlexureStage("/dev/ttyUSB0") as stage:

        gain = [1, 25, 428, 9876]
        stage.light_sensor_gain = 9876
        step_size = 500
        min_step = 50
        points = 10
        samples = 10
        m = 1

        backlash = 256

        df = data_file.Datafile(filename = "hillwalk.hdf5")
        data_intensity = df.new_group("intensity reading", "hill walk")

        intensity_data = np.zeros((500, 5))

        start_time = time.time()
        
        intensity_data[0, 0] = start_time
        intensity_data[0, 1] = stage.light_sensor_fullspectrum
        intensity_data[0, 2:] = stage.position

        while step_size > min_step:
            for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
                    data = take_data(stage, points, samples, direction, step_size, axis)
                    print data
                    for i in range(data.shape[0]):
                        if data[i, 0] < 10:
                            current_gain = stage.light_sensor_gain
                            if current_gain < np.max(gain):
                                stage.light_sensor_gain = np.min([g for g in gain if g > current_gain])
                                continue
                        elif data[i, 0] > 2**15:
                            current_gain = stage.light_sensor_gain
                            if current_gain > np.min(gain):
                                stage.light_sensor_gain = np.max([g for g in gain if g < current_gain])
                                continue
                        else:
                            pass
                    coe = np.polyfit(np.dot(data[:, 2:], axis), data[:, 0], 2)
                    if coe[0] = 0:
                        if coe[1] > 0
                        stage.move_abs(data[points-1, 2:])
                        break
                        elif coe[1] < 0
                        stage.move_abs(data[0, 2:])
                        break
                    elif coe[0] != 0:
                        pos_to_be = -(coe[1] / 2 * coe[0])
                        stage.move_rel(np.dot((pos_to_be - np.dot(data[points-1, 2:], axis)), axis))
                        break
                
            step_size = np.rint(step_size / 2)

        df.add_data(data, data_intensity, "intensity reading")