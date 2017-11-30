#import libraries
import numpy as np
from openflexure_stage import OpenFlexureStage
import time

if __name__ == "__main__":

    with OpenFlexureStage('/dev/ttyUSB0') as stage:
        
          for gain in [1,25,428,9876] :
              
                stage.light_sensor_gain = gain
                
                n = 100
                
                data = np.zeros(n)
     
                for i in range(n):
                    data[i] = stage.light_sensor_fullspectrum
                    time.sleep(10)
             
                mean = np.mean(data)
                error = np.var(data)
                
                print "When gain = %d: \nMean background signal = %d +/- %d \n" % (gain, mean, error) 
