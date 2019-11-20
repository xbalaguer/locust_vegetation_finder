
import picamera
from picamera import PiCamera
import picamera.array
import cv2


class CameraInterface:

    def __init__(self):
        self.camera = PiCamera()

        # camera.iso = 150
        # camera.shutter_speed = 150
        # camera.exposure_mode = 'off'

    def capture_frame(self):     # capture frame and return three arrays, one for each spectrum bands

        img = picamera.array.PiRGBArray(self.camera).array

        # img = cv2.imread(picamera.capture('jpeg'))

        b, g, r = cv2.split(img)

        return r, g, b

    def save_image(self, newfile, image):

        cv2.imwrite(newfile, image)

        return






