
from openflexure_stage import OpenFlexureStage
import numpy as np
import h5py
import time
import data_file
from operator import itemgetter

def take_data(gain, direction, step_size, axis, k, stage):
    data = np.zeros((11, 5))
    avgs = np.zeros(5)
    i = 0
    reading = stage.light_sensor_fullspectrum
    print reading
    gainchange(reading, gain)
    data[i,0] = reading
    data[i,1] = stage.light_sensor_gain
    data[i,2:] = stage.position
    for i in range(data.shape[0]-1):
        stage.move_rel(np.dot(direction * step_size, axis))
        reading = stage.light_sensor_fullspectrum
        gainchange(reading, gain)
        for j in range(avgs.shape[0]):
            avgs[j] = stage.light_sensor_fullspectrum
            time.sleep(1)
        print np.mean(avgs)
        data[i+1,0] = np.mean(avgs)
        data[i+1,1] = stage.light_sensor_gain
        data[i+1,2:] = stage.position
        if abs(data[i+1,0] - data[i,0]) < 50:
            i=i-1
    analysis(data, direction, k, stage)

def analysis(data, direction, k, stage):
    while(k < 2):
        if np.all(np.sign(np.diff(data[:, 0]))) == 1:
            sorted = data[data[:, 0].argsort()]
            print sorted
            stage.move_abs(sorted[data.shape[0]-1, 2:])
            reading = stage.light_sensor_fullspectrum
            print reading
            return reading
        elif np.all(np.sign(np.ediff1d(data[:,0]))) == -1:
            k = k + 1
            direction = direction * -1
            take_data(gain, direction, step_size, axis, k, stage)
        else:
            pass
    pass

def gainchange(reading, gain):
    if reading < 10:
        current_gain = stage.light_sensor_gain
        if current_gain < np.max(gain):
            stage.light_sensor_gain = np.min([g for g in gains if g > current_gain])
            take_data(gain, direction, step_size, axis, k, stage)
    elif reading > 2**15:
        current_gain = stage.light_sensor_gain
        if current_gain > np.min(gain):
            stage.light_sensor_gain = np.max([g for g in gains if g < current_gain])
            take_data(gain, direction, step_size, axis, k, stage)
    else:
        pass

if __name__ == "__main__":
    with OpenFlexureStage("/dev/ttyUSB0") as stage:

        gain = [1, 25, 428, 9876]
        stage.light_sensor_gain = 9876
        step_size = 500
        min_step = 1
        j = 0

#        backlash = 256

        df = data_file.Datafile(filename = "hillwalk.hdf5")
        data_intensity = df.new_group("intensity reading", "hill walk")

        intensity_data = np.zeros((2, 100))

        start_time = time.time

        while step_size > min_step:
            for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
                direction = 1
                k = 0
                take_data(gain, direction, step_size, axis, k, stage)
#                intensity_data[0, j] = time.time - start_time
#                intensity_data[1, j] = reading
                j = j + 1
                step_size = np.rint(step_size / 2)
        
        print stage.position

#        df.add_data(intensity_data, data_intensity, "intensity reading")
