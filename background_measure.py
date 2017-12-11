#import libraries
import numpy as np
from openflexure_stage import OpenFlexureStage
import time
from contextlib import closing
import h5py
import data_file

if __name__ == "__main__":

    with OpenFlexureStage('/dev/ttyUSB0') as stage, closing(data_file.Datafile(filename="background.hdf5")) as df:
        n = 200
        output = np.zeros((2,n))
        data_gr = df.new_group("data", "A file of data collected")
        for gain in [1,25,428,9876] :
            gain_group = df.new_group("Gain", "Measurements for one gain", parent=data_gr)
            stage.light_sensor_gain = gain
            data = np.zeros(n)
            for i in range(n):
                data[i] = stage.light_sensor_fullspectrum
                time.sleep(5)
                
            mean = np.mean(data)
            error = np.std(data)
            print "When gain = %d: \nMean background signal = %d +/- %d \n" % (gain, mean, error)
            df.add_data(data, gain_group, "data")
            
            
        
        
