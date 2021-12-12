import argparse
from datetime import datetime
from math import floor
from multiprocessing import Process
import os
import psutil
from signal import signal, SIGINT
from sys import exit
from time import sleep, time

script_version = '1.0.0'

# Setup argument parser
parser = argparse.ArgumentParser(description='Simple python script that monitors the batteries state of charge', prog='BatterySoCMonitor')
parser.add_argument('--version', action='version', version='%(prog)s ' + script_version)
parser.add_argument('-d', '--delay',
    metavar='',
    type=int,
    default=60,
    help='Delay (in seconds) between each measurement')
parser.add_argument('-v', '--verbose',
    action='store_true',
    help='Print more information')
parser.add_argument('-b', '--beautify',
    action='store_true',
    help='Print information in human readable form')
parser.add_argument('-l', '--log_file',
    metavar='',
    help='Filename of the log-file')
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
parser.add_argument('--cmd_start',
    metavar='',
    help='Command that will be executed when the script starts')
parser.add_argument('--cmd_end',
    metavar='',
    help='Command that will be executed when the script terminates')
parser.add_argument('-w', '--workers',
    nargs='+',
    choices=['cpuLoad'],
    help='Specify a list of worker jobs. Each worker creates a new process')
args = parser.parse_args()


worker_threads = []


def worker_cpuLoad():
    x = 123
    while True:
        x*x


def seconds_to_human_form(seconds):
    if seconds < 0:
        return '00:00:00?'

    hours_int = floor(seconds / 3600)
    if hours_int < 10:
        hours_str = '0'
    else:
        hours_str = ''
    hours_str += str(hours_int)

    minutes_int = floor((seconds % 3600) / 60)
    if minutes_int < 10:
        minutes_str = '0'
    else:
        minutes_str = ''
    minutes_str += str(minutes_int)

    seconds_int = (seconds % 3600) % 60
    if seconds_int < 10:
        seconds_str = '0'
    else:
        seconds_str = ''
    seconds_str += str(seconds_int)

    return hours_str  + ':' + minutes_str + ':' + seconds_str


def soc_to_human_form(soc):
    soc_0 = floor(soc)
    soc_1 = int((soc - soc_0) * 100)

    soc_str = ''
    if soc_0 < 10:
        soc_str += '  '
    elif soc_0 < 100:
        soc_str += ' '

    soc_str += str(soc_0) + '.' + str(soc_1)

    if soc_1 < 10:
        soc_str += '0%'
    else:
        soc_str += '%'

    return soc_str


def myPrint(*strings, sep=' ', end='\n'):
    combined_string = ''

    if len(strings) > 1:
        for i in range(0, len(strings) - 1):
            combined_string += str(strings[i]) + sep


    if len(strings) > 0:
        combined_string += str(strings[-1]) + end
    else:
        combined_string += end

    print(combined_string, end='')

    if args.log_file != None:
        with open(args.log_file, 'a+') as f:
            f.write(combined_string)


def main():
    global worker_threads

    # execute start command
    if args.cmd_start != None:
        os.system(args.cmd_start)

    if args.verbose:
        if args.beautify:
            myPrint('timeExecuted\tbat %\ttimeRemaining')
            myPrint('hh:mm:ss\t\thh:mm:ss')
            myPrint('---------\t-------\t---------')
        else:
            myPrint('<secs>      : seconds since script was started')
            myPrint('<soc>       : batteries state of charge')
            myPrint('<secs_left> : prediction on battery time left')
            myPrint()
            myPrint('<secs>\t<soc>\t<secs_left>')

    time_start = time()

    # create and start worker thread(s)
    if args.workers != None:
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
        time_executed = round(time_now - time_start)

        if args.beautify:
            myPrint(seconds_to_human_form(time_executed), soc_to_human_form(state_of_charge), seconds_to_human_form(seconds_left), sep='\t')
        else:
            myPrint(time_executed, state_of_charge, seconds_left, sep='\t')

        if state_of_charge <= args.minimum_soc:
            if args.verbose:
                myPrint('Batteries state of charge reached the minimum level. Terminating script.')
            end(None, None)
        if state_of_charge >= args.maximum_soc:
            if args.verbose:
                myPrint('Batteries state of charge reached the maximum level. Terminating script.')
            end(None, None)

        sleep(args.delay - (time_now - time_start) % args.delay) # execution time compensation


def end(signal_received, frame):
    # stop all worker threads
    global worker_threads
    for wt in worker_threads:
        wt.terminate()

    # execute end command
    if args.cmd_end != None:
        os.system(args.cmd_end)

    if args.verbose:
        myPrint('Goodbye!')
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, end)
    main()
    end(None, None)
