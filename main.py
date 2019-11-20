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
import json
import datetime


def image_correction(heading, pitch, roll, latitude, longitude, height):  # function to obtain real coordinates of photo vertices

    coordinates = [ul, ur, dl, dr]    # ul is upper left vertex GPS coordinates
    return image, coordinates


"""things to implement: 
- With a given folder for the generated data, create folders with the datatime, and inside there, create one for 
the images and store there the txt file with the JSON 

"""


def main_loop(camera_interface, autopilot_interface):

    r, g, b = camera_interface.capture_frame()

    difference = r - b
    summatory = r + b

    ndvi = difference / summatory

    y = 0      # y gives us the total number of values that are following ndvi condition
    i = 0

    while i in range(ndvi[0]):
        j = 0
        while j in range(ndvi[1]):
            if ndvi[i,j] > 0.2:
                y += 1
                j += 1
            else:
                j += 1
        i += 1

    total_values = ndvi.shape[0] * ndvi.shape[1]  # we multiply the number of rows by the number of columns to obtain
                                                  # the total number of values

    percent = y / total_values

    # check all the values in the array ndvi

    # percent of values with ndvi > xxxx

    if percent >= 0.1:

        timestamp = datetime.datetime.now()

        latitude = autopilot_interface.get_latitude()
        longitude = autopilot_interface.get_longitude()
        pitch = autopilot_interface.get_pitch()
        altitude = autopilot_interface.get_altitude()

        output_file = open('time.txt', 'x')

        data['drone'] = {'timestamp': timestamp,
                         'latitude': latitude,
                         'longitude': longitude,
                         'altitude': altitude,
                         'pitch': pitch, }

        information = json.dumps(data)

        with output_file as f:
            f.write(information)

        # convert ndvi array to a photo again and store it
        # store the original photo

        # write in a JSON all the important values (timestamp, gps coordinates, altitude, percent)
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
    parser.add_argument("--file", dest="output_file", default= "", help="images folder")
    parser.add_argument("-v", "--video", help="path to the (optional) video file")

    # parser.add_argument("--drone", dest="drone", default="HDR001", help="license plate of the dronea")
    # parser.add_argument("--rate", dest="rate", default=4, type='int', help="requested stream rate")
    # parser.add_argument("--source-system", dest='SOURCE_SYSTEM', type='int',
                     # default=255, help='MAVLink source system for this GCS')

    #parser.add_argument("--showmessages", dest="showmessages", action='store_true',
                     # help="show incoming messages", default=False)

    args = parser.parse_args()

    return args


def main():


    # Add parsing of configuration file
    #parser = create_parser()

    opts, args = create_parser()

    camera_interface = CameraInterface()

    autopilot_interface = AutopilotInterface()

    if opts.device is None:
        TerminalMessage.print_msg("You must specify a serial device", level=ERROR, header=LOGGER_HEADER, color_header=LOGGER_COLOR)
        sys.exit(1)




    main_loop(camera_interface, autopilot_interface)


if __name__ == '__main__':
    main()