import argparse
from datetime import datetime
import psutil
from signal import signal, SIGINT
from sys import exit
from time import sleep, time


# Setup argument parser
parser = argparse.ArgumentParser(description='Simple python script that monitors the batteries state of charge', prog='BatterySoCMonitor')
parser.add_argument('--version', action='version', version='%(prog)s v0.0.1')
parser.add_argument('-d', '--delay',
    metavar='',
    type=int,
    default=60,
    help='Delay (in seconds) between each measurement.')
parser.add_argument('-v', '--verbose',
    action='store_true',
    help='Print more information')
args = parser.parse_args()


def main():
    if args.verbose:
        print('----------')
        print('Script startet at:\t\t', datetime.now(), sep='')
        print('delay between measurements:\t', args.delay, sep='')
        print('----------')
        print()
        print('<secs>      : seconds since script was started')
        print('<soc>       : batteries state of charge')
        print('<secs_left> : prediction on battery time left')
        print()
        print('<secs>\t<soc>\t<secs_left>')

    time_start = time()
    while True:
        time_now = time()
        battery = psutil.sensors_battery()
        state_of_charge = round(battery.percent, 2)
        seconds_left = round(battery.secsleft)
        print(round(time_now - time_start), state_of_charge, seconds_left, sep='\t')
        sleep(args.delay - (time_now - time_start) % args.delay) # execution time compensation

def end(signal_received, frame):
    print('Goodbye!')
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, end)
    main()
