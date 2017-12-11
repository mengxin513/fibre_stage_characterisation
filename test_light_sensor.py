from openflexure_stage import OpenFlexureStage
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    with OpenFlexureStage("COM4") as stage:
    #with OpenFlexureStage("/dev/ttyUSB1") as stage:
        gains = stage.light_sensor_gain_values
        print gains
        f, axes = plt.subplots(1,len(gains))
        for i in range(len(gains)):
            stage.light_sensor_gain = gains[i]
            print "Gain is {}".format(stage.light_sensor_gain)
            #print "Integration time is {} ms".format(stage.light_sensor_integration_time)
            print "Reading sensor",
            readings = np.zeros(50)
            for j in range(len(readings)):
                readings[j] = stage.light_sensor_intensity
                print ".",
            print "done"
            print "reading {}+/-{}".format(np.mean(readings), np.std(readings))
            axes[i].plot(readings)
    plt.show()