from optparse import OptionParser


def create_parser():
    # read command line options
    parser = OptionParser("readdata.py [options]")
    parser.add_option("--baudrate", dest="baudrate", type='int',
                      help="master port baud rate",
                      default=57600)  # for USB connection is 115200, for the port "telem2" of PX4 is 57600
    parser.add_option("--device", dest="device", default="/dev/ttyUSB0", help="serial device")
    parser.add_option("--drone", dest="drone", default="HDR001", help="license plate of the dronea")
    parser.add_option("--rate", dest="rate", default=4, type='int', help="requested stream rate")
    parser.add_option("--source-system", dest='SOURCE_SYSTEM', type='int',
                      default=255, help='MAVLink source system for this GCS')
    parser.add_option("--showmessages", dest="showmessages", action='store_true',
                      help="show incoming messages", default=False)

    return parser

def main():

    parser = create_parser()

    (opts, args) = parser.parse_args()