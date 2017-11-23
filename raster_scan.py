
from openflexure_stage import OpenFlexureStage
import numpy as np

if __name__ == "__main__":
    with OpenFlexureStage("/dev/ttyUSB0") as stage:

        gain = 1
        radius = 0

        backlash = None

        reading = stage.light_sensor_fullspectrum

        while(reading == 0):
            while(radius < 1000):
                for angle in range(360):
                    stage.move_rel([radius*np.cos(angle * np.pi / 180), radius*np.sin(angle * np.pi / 180), 0]) #moves in a circle
                    reading = stage.light_sensor_fullspectrum #takes a reading after each degree of movement
                radius = radius + 10

        stage_position = stage.position
