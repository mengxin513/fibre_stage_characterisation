from __future__ import print_function
import picamera
import picamera.array
import numpy as np
import time
import matplotlib.pyplot as plt

if __name__ == "__main__":
    with picamera.PiCamera(resolution=(1280,960)) as cam:
        cam.start_preview()
        time.sleep(2) #do the auto-stuff
        rgb_array_v = picamera.array.PiRGBArray(cam)
        rgb_array_s = picamera.array.PiRGBArray(cam)
        bayer_array = picamera.array.PiBayerArray(cam)
        cam.capture(rgb_array_v, format="rgb", use_video_port=True)
        cam.capture(rgb_array_s, format="rgb", use_video_port=False)
        cam.capture(bayer_array, format="jpeg", bayer=True)
        bayer = bayer_array.array
        rgb_v = rgb_array_v.array
        rgb_s = rgb_array_s.array

        # Very dirty: downsample 2x2, to get rid of empty pixels
        shrunk_debayered = np.sum(np.stack([bayer[i::2,j::2,:]//[4,8,4] for i in range(2) for j in range(2)]).astype(np.uint8), axis=0)
        # Also very dirty: correct RGB gains vs non-raw image:
        gain_correction = np.mean(rgb_s, axis=(0,1))/np.mean(shrunk_debayered, axis=(0,1))
        rgb_from_raw = (shrunk_debayered * gain_correction).astype(np.uint8)
        gray_from_raw = np.sum(bayer//4 * gain_correction, axis=2).astype(np.uint8)

        cam.stop_preview()
        
        f, axes = plt.subplots(2,2)
        axes[0,0].imshow(rgb_v)
        axes[0,1].imshow(rgb_s)
        axes[1,0].imshow(gray_from_raw)
        axes[1,1].imshow(rgb_from_raw)
        plt.show()


