
from openflexure_stage import OpenFlexureStage
import numpy as np
import h5py
import data_file

if __name__ == "__main__":
    with OpenFlexureStage("/dev/ttyUSB0") as stage:

        gain = 9876 #maximum gain to detect faint signal
        length = 100 #initial side length of spiral
        step = 10 #move distance per step
        move = 0 #distance already moved
        i = 0 #counter

        backlash = None

        df = data_file.Datafile(filename = "raster.hdf5")
        data_intensity = df.new_group("intensity reading", "raster scan")
        data_stage = df.new_group("stage position", "raster scan")

        intensity_data = np.zeros((1, 5000))
        stage_data = np.zeros((3, 5000))

        reading = stage.light_sensor_fullspectrum
        stage_position = stage.position
        intensity_data[0, i] = reading
        stage_data[0:, i] = stage_position
        i = i + 1
        print reading

        while(reading < 100): #avoids background noise
            while(move <= length):
                stage.move_rel([step, 0, 0])
                reading = stage.light_sensor_fullspectrum #takes a reading after each degree of movement
                intensity_data[0, i] = reading
                stage_position = stage.position
                stage_data[0:, i] = stage_position
                move = move + step
                i = i + 1
                print reading
            length = length + 30
            move = 0
            while(move <= length):
                stage.move_rel([0, step, 0])
                reading = stage.light_sensor_fullspectrum
                intensity_data[0, i] = reading
                stage_position = stage.position
                stage_data[0:, i] = stage_position
                move = move + step
                i = i + 1
                print reading
            length = length + 30
            move = 0
            while(move <= length):
                stage.move_rel([-step, 0, 0])
                reading = stage.light_sensor_fullspectrum
                intensity_data[0, i] = reading
                stage_position = stage.position
                stage_data[0:, i] = stage_position
                move = move + step
                i = i + 1
                print reading
            length = length + 30
            move = 0
            while(move <= length):
                stage.move_rel([0, -step, 0])
                reading = stage.light_sensor_fullspectrum
                intensity_data[0, i] = reading
                stage_position = stage.position
                stage_data[0:, i] = stage_position
                move = move + step
                i = i + 1
                print reading
            length = length + 30
            move = 0

        df.add_data(intensity_data, data_intensity, "intensity reading")
        df.add_data(stage_data, data_stage, "stage position")
