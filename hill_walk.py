
from openflexure_stage import OpenFlexureStage
import numpy as np
import h5py
import time
import data_file

def take_data(gain, direction, step_size, axis):
    data = np.zeros((5, 6))
    i = 0
    reading = stage.light_sensor_fullspectrum
    gainchange(reading, gain)
    data[0, i] = reading
    data[1, i] = stage.light_sensor_gain
    data[2:, i] = stage.position
    for i in range(5):
        stage.move_rel(direction * step_size * axis)
        reading = stage.light_sensor_fullspectrum
        gainchange(reading, gain)
        data[0, i] = reading
        data[1, i] = stage.light_sensor_gain
        data[2:, i] = stage.position
    analysis(data, direction)

def analysis(data, direction):
    while(k < 2):
        if np.all(np.sign(np.ediff1d(data[0, :]))) == 1:
            data[data[:,0].argsort()]
            stage.move_abs(data[1:, 6])
            reading = stage.light_sensor_fullspectrum
            return reading
        elif np.all(np.sign(np.ediff1d(data[0, :]))) == -1:
            k = k + 1
            direction = direction * -1
            take_data(gain, direction, step_size, axis)
        else:
            pass
    pass

def gainchange(reading, gain):
    if reading < 10:
        current_gain = stage.light_sensor_gain
        if current_gain < np.max(gain):
            stage.light_sensor_gain = np.min([g for g in gains if g > current_gain])
    if reading > 2**15:
        current_gain = stage.light_sensor_gain
        if current_gain > np.min(gain):
            stage.light_sensor_gain = np.max([g for g in gains if g < current_gain])
    take_data(gain, direction, step_size, axis)

if __name__ == "__main__":
    with OpenFlexureStage("/dev/ttyUSB0") as stage:

        gain = [1, 25, 428, 9876]
        stage.light_sensor_gain = 9876
        step_size = 100
        min_step = 1
        j = 0

        backlash = 256

        df = data_file.Datafile(filename = "hillwalk.hdf5")
        data_intensity = df.new_group("intensity reading", "hill walk")

        intensity_data = np.zeros((2, 100))

        start_time = time.time

        while step_size > min_step:
            for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
                direction = 1
                k = 0
                take_data(gain, direction, step_size, axis)
                intensity_data[0, j] = time.time() - start_time
                intensity_data[1, j] = reading
                j = j + 1
                step_size = np.rint(step_size / 2)

        df.add_data(intensity_data, data_intensity, "intensity reading")
