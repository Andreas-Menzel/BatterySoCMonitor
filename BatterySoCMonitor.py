import argparse
from datetime import datetime
from multiprocessing import Process
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
parser.add_argument('--minimum_soc',
    metavar='',
    type=int,
    default=5,
    help='Terminate script when batteries state of charge is below or equal to this percentage')
parser.add_argument('--maximum_soc',
    metavar='',
    type=int,
    default=101,
    help='Terminate script when batteries state of charge is above or equal to this percentage')
parser.add_argument('-w', '--workers',
    nargs='+',
    choices=['cpuLoad'],
    help='Specify a list of worker jobs.')
args = parser.parse_args()


worker_threads = []


def worker_cpuLoad():
    x = 123
    while True:
        x*x


def main():
    global worker_threads

    if args.verbose:
        print('<secs>      : seconds since script was started')
        print('<soc>       : batteries state of charge')
        print('<secs_left> : prediction on battery time left')
        print()
        print('<secs>\t<soc>\t<secs_left>')

    time_start = time()

    # create and start worker thread(s)
    for w in args.workers:
        if w == 'cpuLoad':
            worker_threads.append(Process(target=worker_cpuLoad))

    for wt in worker_threads:
        wt.start()

    while True:
        time_now = time()
        battery = psutil.sensors_battery()
        state_of_charge = round(battery.percent, 2)
        seconds_left = round(battery.secsleft)
        print(round(time_now - time_start), state_of_charge, seconds_left, sep='\t')

        if state_of_charge <= args.minimum_soc:
            if args.verbose:
                print('Batteries state of charge reached the minimum level. Terminating script.')
            end(None, None)
        if state_of_charge >= args.maximum_soc:
            if args.verbose:
                print('Batteries state of charge reached the maximum level. Terminating script.')
            end(None, None)

        sleep(args.delay - (time_now - time_start) % args.delay) # execution time compensation


def end(signal_received, frame):
    # stop all worker threads
    global worker_threads
    for wt in worker_threads:
        wt.terminate()

    if args.verbose:
        print('Goodbye!')
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, end)
    main()
    end(None, None)
