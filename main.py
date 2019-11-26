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
import time
import numpy as np
import os
import json
import pandas as pd


def image_correction(heading, pitch, roll, latitude, longitude, height):  # function to obtain real coordinates of photo vertices

    coordinates = [ul, ur, dl, dr]    # ul is upper left vertex GPS coordinates
    return image, coordinates


def write_image_data(output_file, data_drone, data_image):   # function for writing the image data as a json in a txt file

    year = pd.datetime.now().year
    month = pd.datetime.now().month
    day = pd.datetime.now().day
    hour = pd.datetime.now().hour
    minute = pd.datetime.now().minute
    seconds = pd.datetime.now().second

    latitude = data_drone[0]
    longitude = data_drone[1]
    pitch = data_drone[2]
    altitude = data_drone[3]

    percent = data_image[0]

    data = {}
    data['image data'] = []

    data['image data'].append({
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': seconds,
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'pitch': pitch,
        'Vegetation percent': percent,
    })

    json.dump(data, output_file)

    return


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


def main_loop(camera_interface, autopilot_interface):

    r, g, b = camera_interface.capture_frame()

    np.seterr(divide='ignore', invalid='ignore')

    ndvi = (r - b) / (b + r)

    y = 0  # y gives us the total number of values that are following ndvi condition
    i = 0

    while i < ndvi.shape[0]:
        j = 0
        while j < ndvi.shape[1]:
            if ndvi[i, j] > 0.2:
                y += 1
                j += 1
            else:
                j += 1
        i += 1

    total_values = ndvi.shape[0] * ndvi.shape[1]  # we multiply the number of rows by the number of columns to obtain
    # the total number of values

    percent = (y / total_values) * 100

    if percent >= 0.1:

        output_file = open('time.txt', 'x')

        data_drone = autopilot_interface.set_data_drone()
        
        data_image = [percent, photo_number]

        write_image_data(output_file, data_drone, data_image)

        # convert ndvi array to a photo again and store it
        # store the original photo
        # save the image correctly

    else:
        # discard actual data
        time.sleep(3)

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

    # Add parsing of configuration file
    # parser = create_parser()

    opts, args = create_parser()

    camera_interface = CameraInterface()

    autopilot_interface = AutopilotInterface()

    if opts.device is None:
        TerminalMessage.print_msg("You must specify a serial device", level=ERROR, header=LOGGER_HEADER, color_header=LOGGER_COLOR)
        sys.exit(1)

    main_loop(camera_interface, autopilot_interface)


if __name__ == '__main__':
    main()