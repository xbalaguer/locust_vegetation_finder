"""
Created on Thu Nov 14 11:30 2019

This code has to recognise vegetation in the dessert using a NIR raspberry pi camera and processing images with a raspberry.

For this reason, we need:
    1) Connect the camera to the raspberry and the raspberry to the Pixhawk
    2) Take images every XXX seconds
    3) Split the image in the 3 bands. for each image, we will obtain 3 arrays. By operating with this arrays, we compute the NDVI
    4) If the NDVI is higher that XXX value, we need to connect contact the pixhawk in order to obtain GPS data.
    5) A txt file should be generated will all the necessary data or the application

"""

from optparse import OptionParser
from libs.terminalMessage import TerminalMessage, Color
import argparse
from interfaces.autopilot_interface import AutopilotInterface
from interfaces.camera_interface import CameraInterface
import numpy as np
import os
import json
import pandas as pd
import cv2
import math


def footprint():

    # Camera carachteristics:

    # Sensor (mm)
    sx = 3.68
    sy = 2.76

    # Focal length of lens (mm)
    fl = 3.04

    # Pixels
    px = CameraInterface.camera.resolution[1]
    py = CameraInterface.camera.resolution[0]

    pixels_camera = px * py

    # Field of view wide (gra)
    HFOV = 62.2
    # HFOV = math.radians(HFOV)
    HFOVcal = 2 * math.atan(sx / (2 * fl))
    # HFOVcal = math.degrees(HFOVcal)
    # Field of view tall (gra)
    VFOV = 48.8
    # VFOV = math.radians(VFOV)
    VFOVcal = 2 * math.atan(sy / (2 * fl))
    # VFOVcal = math.degrees(VFOVcal)

    pitch = math.radians(AutopilotInterface.get_pitch())
    roll = math.radians(AutopilotInterface.get_roll())
    # FOOTPRINT(m)

    # Footprint needs to be well calculated
    fy2 =
    fx2 =
    footprint = fy2 * fx2

    return footprint

def initialize_json(timestamp):

    global data
    global flights
    global results
    global flight

    data = {}
    flights = {}
    results = {}

    data["flights"] = []

    flight = {
        "id": timestamp,
        "results": []
    }

    data["flights"].append(flight)

    print('Json initialized')

def write_json(num, percentage, data_drone, image_settings, path):

    coordinates = [data_drone[0], data_drone[1]]

    settings = image_settings

    image_data = {
        "image_id": num,
        "percentage": percentage,
        "coordinates": coordinates,
        "path": path,
        "settings": settings
        }

    flight["results"].append(dict(image_data))
    print(data)


def close_json(output_file):
    with output_file as f:
        json.dump(data, f)

        f.close()

    print("done")



def create_directory():  # tested and working

    path = os.getcwd()  # this returns actual directory as a string (should be modify to a raspberry directory)

    # we need to convert numbers to string to be able to create the new path
    year = str(pd.datetime.now().year)
    month = str(pd.datetime.now().month)
    day = str(pd.datetime.now().day)
    hour = str(pd.datetime.now().hour)
    minute = str(pd.datetime.now().minute)

    newpath = path + "/" + year + "_" + month + "_" + day + "-" + hour + "_" + minute  # we create the string for the new directory

    os.mkdir(newpath)        # creates a directory

    return

def contrast_stretch(im):
    """
    Performs a simple contrast stretch of the given image, from 5-95%.
    """
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

def main_loop(camera_interface, autopilot_interface):

    img = camera_interface.capture_frame()

    # We want a smoother image to have a better processing results
    median = cv2.medianBlur(img, 5)

    # We convert the image to HSV to isolate the vegetation
    hsv_image = cv2.cvtColor(median, cv2.COLOR_BGR2HSV)

    # define range in HSV to create a mask that will be applied to the original image
    lower_limit = np.array([110, 130, 160])
    upper_limit = np.array([255, 200, 255])

    # Threshold the HSV image to get only vegetation
    mask_red = cv2.inRange(hsv_image, lower_limit, upper_limit)

    #We process the obtained mask in order to reduce noise in the image
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

    kernel = np.ones((8, 8), np.uint8)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    mask_red = closing

   # Once we have a gray colorspace mask, we want to add the original image to it
    img2 = cv2.bitwise_and(img, img, mask=mask_red)

    # Colorbands of the original image containing vegetation
    b = np.array(img2[:, :, 0]).astype(float) + 0.00000000001
    g = np.array(img2[:, :, 1]).astype(float)
    r = np.array(img2[:, :, 2]).astype(float) + 0.00000000001

    nir = b
    red = r
    np.seterr(divide='ignore', invalid='ignore')

    ndvi = ((nir - red) / (nir + red)).astype(float)

    #Once we have the ndvi matrix, we want to know how many values are following the ndvi condition
    values_ndvi = np.count_nonzero(ndvi > 0.2)

    # we multiply the number of rows by the number of columns to obtain the total number of values
    total_values = ndvi.shape[0] * ndvi.shape[1]

    percent = round(((values_ndvi / total_values) * 100), 2)

    if percent > 10:

        # We normalize the ndvi matrix between 0 and 255 values to have a good drawing
        ndvi_new = contrast_stretch(ndvi).astype(np.uint8)

        # We apply a colormap to the final NDVI matrix
        ndvi_final = cv2.applyColorMap(ndvi_new, cv2.COLORMAP_JET)

        # We create a mask with the image region that has no vegetation
        res = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask_red))
        ndvi_final = cv2.bitwise_and(ndvi_final, ndvi_final, mask=mask_red)

        # We join both NDVI final representation and the no-vegetation part of the image
        fusion = res + ndvi_final

        path = os.getcwd()
        name = path + '/' + 'ndvi_results' + '/' + 'image' + 'ndvi' + str(percent) + '.jpeg'

        cv2.imwrite(name, fusion)

        output_file = open('results.json', 'x')


        data_drone = autopilot_interface.set_data_drone()

        image_settings = camera_interface.camera_settings()

        write_json(num, percent, data_drone, image_settings, name)

        close_json(output_file)

        # store the original photo
        # save the image correctly

    return


def create_parser():

    # read command line options

    #parser = OptionParser("readdata.py [options]")

    parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')

    parser.add_argument("--baudrate", dest="baudrate", type='int',
                      help="master port baud rate", default=57600)  # for USB connection is 115200, for the port "telem2" of PX4 is 57600
    parser.add_argument("--device", dest="device", default="/dev/ttyAMA0", help="serial device")
    parser.add_argument("--file", dest="output_file", default="", help="images folder")
    parser.add_argument("-v", "--video", help="path to the (optional) video file")

    # parser.add_argument("--drone", dest="drone", default="HDR001", help="license plate of the dronea")
    # parser.add_argument("--rate", dest="rate", default=4, type='int', help="requested stream rate")
    # parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type='int',
                     # default=255, help='MAVLink source system for this GCS')

    #parser.add_argument("--showmessages", dest="showmessages", action='store_true',
                     # help="show incoming messages", default=False)

    opts, args = parser.parse_args()

    return opts, args


def main():

    global num
    num = 1

    camera_interface = CameraInterface()

    autopilot_interface = AutopilotInterface()

    main_loop(camera_interface, autopilot_interface)

    num += 1

if __name__ == '__main__':
    main()