
import picamera
from picamera import PiCamera
import picamera.array
import cv2
import numpy as np


class CameraInterface:

    def __init__(self):
        self.camera = PiCamera()

        # camera.iso = 150
        # camera.shutter_speed = 150
        # camera.exposure_mode = 'off'

    def capture_frame(self):     # capture frame and return three arrays, one for each spectrum bands

        img = picamera.array.PiRGBArray(self.camera).array

        # img = cv2.imread(picamera.capture('jpeg'))

        # b, g, r = cv2.split(img)

        b = np.array(img[:, :, 0]).astype(float) + 0.00000000001
        g = np.array(img[:, :, 1]).astype(float)
        r = np.array(img[:, :, 2]).astype(float) + 0.00000000001

        return r, g, b

    def save_image(self, newfile, image):

        cv2.imwrite(newfile, image)

        return





