
import cv2
import numpy as np
from scipy import ndimage, signal
import time
from camera_stuff import get_numpy_image, find_template
import microscope
import picamera
import data_file
from openflexure_stage import OpenFlexureStage
import data_file
import h5py
import tweepy
import twitter_keys
from contextlib import closing

if __name__ == "__main__":

    with picamera.PiCamera(resolution = (640, 480)) as camera, \
         OpenFlexureStage('/dev/ttyUSB0') as stage, \
         closing(data_file.Datafile(filename = "drift.hdf5")) as df:

        #authorises the program to acces the twitter account
        auth = tweepy.OAuthHandler(twitter_keys.consumer_key, twitter_keys.consumer_secret)
        auth.set_access_token(twitter_keys.access_token, twitter_keys.access_token_secret)
        api = tweepy.API(auth)
        
        N_frames = 100

        ms = microscope.Microscope(camera, stage)
        ms.freeze_camera_settings()
        frame = get_numpy_image(camera, True)

        df = data_file.Datafile(filename = "drift.hdf5")
        cam_pos = df.new_group("data", "drift")

        loop = True
        tweet = True

        image = get_numpy_image(camera, greyscale = True).astype(np.float32)
        background = cv2.GaussianBlur(image, (41, 41), 0)
        templ8 = (image - background)[100:-100, 100:-100]

        start_t = time.time()

        try:
            while loop:
                data = np.zeros((N_frames, 3))
                for i in range(N_frames):
                    frame = get_numpy_image(camera, True)
                    data[i, 1:], corr = find_template(templ8, frame - background, return_corr = True)
                    cv2.imshow("corr", corr.astype(float) / np.max(corr) * 255)
                    cv2.waitKey(1000)
                    data[i, 0] = time.time() - start_t
                df.add_data(data, cam_pos, "data")
                imgfile_location = "/home/pi/dev/fibre_stage_characterisation/frames/drift_%s.jpg" % time.strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(imgfile_location, frame)
                try:
                    if time.gmtime(time.time())[3] in [0, 4, 8, 12, 16, 20] and tweet: #tweets a picture and co-ordinates every 4 hours
                        api.update_with_media(imgfile_location, status = "I'm currently at %d, %d" %(spot_coord[0], spot_coord[1]))
                        tweet = False
                    elif time.gmtime(time.time())[3] not in [0, 4, 8, 12, 16, 20]:
                        tweet = True
                except:
                    pass
        except KeyboardInterrupt:
            print "Got a keyboard interrupt, stopping"
            