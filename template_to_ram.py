import io
from camera_stuff import get_numpy_image, find_template
import picamera
import cv2
import numpy as np
import time
from openflexure_stage import OpenFlexureStage
import threading

with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:

    event = threading.Event() #creates the event for the thread

    def movement(): #defines the function for moving the stage
        global event, stage
        while not event.wait(2):
            stage.move_rel([100,100,100]) #move alternatively in X and Y

    outputs = [io.BytesIO() for j in range(100)] #creates a list containing RAM locations for 100 images

    image = get_numpy_image(camera, greyscale=True) #takes template photo
    templ8 = image[100:-100,100:-100] #crops image

    data = np.zeros((3,100))
    
    camera.start_preview()

    move_thread = threading.Thread(target=movement)

    move_thread.start() #start the movement thread

    print "Wait 10"
    time.sleep(10)
    
    camera.capture_sequence(outputs, 'jpeg', use_video_port=True) #takes a picture and saves to each location in outputs

    event.set()
    print "It's over"

    for i,o in enumerate(outputs):
        frame_data = np.fromstring(o.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(frame_data, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        spot_coord = find_template(templ8, frame)
        data[0,i] = 0
        data[1,i] = spot_coord[0]
        data[2,i] = spot_coord[1]			
        print(data[1,i], data[2,i])