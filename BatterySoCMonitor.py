import argparse
from datetime import datetime
from math import floor
from multiprocessing import Process
import os
from platform import system
import psutil
from signal import signal, SIGINT
from sys import exit
from time import sleep, strftime, time, localtime

script_version = '2.0.2'

# Setup argument parser
parser = argparse.ArgumentParser(description='Simple python script that monitors the batteries state of charge', prog='BatterySoCMonitor')
parser.add_argument('--version', action='version', version='%(prog)s ' + script_version)
parser.add_argument('--sample_rate',
    metavar='',
    type=int,
    help='Delay (in seconds) between each measurement. Must be a divisor of --output_rate')
parser.add_argument('--output_rate',
    metavar='',
    type=int,
    help='Delay (in seconds) between each data output. Must be a multiple of --sample_rate')
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
    default=None,
    help='Terminate script when batteries state of charge is below or equal to this percentage')
parser.add_argument('--maximum_soc',
    metavar='',
    type=int,
    default=None,
    help='Terminate script when batteries state of charge is above or equal to this percentage')
parser.add_argument('--cmd_min_soc',
    metavar='',
    help='Command that will be executed when the script terminates because of the batteries state of charge (see --minimum_soc)')
parser.add_argument('--cmd_max_soc',
    metavar='',
    help='Command that will be executed when the script terminates because of the batteries state of charge (see --maximum_soc)')
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
time_start = None
time_end = None
battery_soc_start = None
battery_soc_end = None
expected_remaining_time_start = None
expected_remaining_time_end = None
median_consumption_start = 0
median_consumption_end = None

data_soc = []
data_secsleft = []
data_median_consumption = []
median_consumption_last_soc_change = None
median_consumption_last_soc = None


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


def percentage_to_human_form(percent):
    percent_0 = floor(percent)
    percent_1 = int((percent - percent_0) * 100)

    percent_str = ''
    if percent_0 < 10:
        percent_str += '  '
    elif percent_0 < 100:
        percent_str += ' '

    percent_str += str(percent_0) + '.' + str(percent_1)

    if percent_1 < 10:
        percent_str += '0%'
    else:
        percent_str += '%'

    return percent_str


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



def clear_previous_line():
    if system() == 'Linux':
        print("\033[F", end='') # Cursor up one line
        print("\033[K", end='') # Clear to the end of line



def main():
    global worker_threads
    global time_start
    global battery_soc_start
    global expected_remaining_time_start
    global median_consumption_start
    global data_soc
    global data_secsleft
    global data_median_consumption
    global median_consumption_last_soc
    global median_consumption_last_soc_change

    # Initialize sample_rate and output_rate
    if args.sample_rate == None and args.output_rate == None:
        args.sample_rate = 10
        args.output_rate = 10
    elif args.sample_rate == None and args.output_rate != None:
        args.sample_rate = args.output_rate
    elif args.sample_rate != None and args.output_rate == None:
        args.output_rate = args.sample_rate
    else:
        if args.output_rate % args.sample_rate != 0:
            myPrint('ERROR: --output_rate must be a multiple of --sample_rate')
            end_error()

    time_start = time()
    battery_soc_start = round(psutil.sensors_battery().percent)
    expected_remaining_time_start = round(psutil.sensors_battery().secsleft)

    # execute start command
    if args.cmd_start != None:
        os.system(args.cmd_start)

    myPrint('# Welcome to BatterySoCMonitor version ', script_version, '!', sep='')

    # print parameter values
    if args.verbose:
        if args.beautify:
            myPrint('# sample_rate', '\t', ':\t', args.sample_rate, sep='')
            myPrint('# output_rate', '\t', ':\t', args.output_rate, sep='')
            myPrint('# verbose', '\t', ':\t', args.verbose, sep='')
            myPrint('# beautify', '\t', ':\t', args.beautify, sep='')
            myPrint('# log_file', '\t', ':\t', args.log_file, sep='')
            myPrint('# minimum_soc', '\t', ':\t', args.minimum_soc, sep='')
            myPrint('# maximum_soc', '\t', ':\t', args.maximum_soc, sep='')
            myPrint('# cmd_start', '\t', ':\t', args.cmd_start, sep='')
            myPrint('# cmd_end', '\t', ':\t', args.cmd_end, sep='')
            myPrint('# workers', '\t', ':\t', args.workers, sep='')
        else:
            myPrint('# sample_rate', '\t', ':\t', args.sample_rate, sep='')
            myPrint('# output_rate', '\t', ':\t', args.output_rate, sep='')
            myPrint('# verbose', ':', args.verbose, sep='\t')
            myPrint('# beautify', ':', args.beautify, sep='\t')
            myPrint('# log_file', ':', args.log_file, sep='\t')
            myPrint('# minimum_soc', ':', args.minimum_soc, sep='\t')
            myPrint('# maximum_soc', ':', args.maximum_soc, sep='\t')
            myPrint('# cmd_start', ':', args.cmd_start, sep='\t')
            myPrint('# cmd_end', ':', args.cmd_end, sep='\t')
            myPrint('# workers', ':', args.workers, sep='\t')

    if args.beautify:
        myPrint()
        myPrint('timeExecuted\tbat %\ttimeRemaining\tconsumption')
        myPrint('hh:mm:ss\t\thh:mm:ss\t(median)')
        myPrint('---------\t-------\t---------\t-----------')
    else:
        myPrint()
        myPrint('# <sec>\t<soc>\t<until>\t<consumption>')

    time_start = time()

    # create and start worker thread(s)
    if args.workers != None:
        for w in args.workers:
            if w == 'cpuLoad':
                worker_threads.append(Process(target=worker_cpuLoad))

        for wt in worker_threads:
            wt.start()

    myPrint()
    sample_counter = 0
    while True:
        time_now = time()
        battery = psutil.sensors_battery()
        state_of_charge = round(battery.percent, 2)
        data_soc.append(state_of_charge) # save data

        seconds_left = round(battery.secsleft)
        data_secsleft.append(seconds_left) # save data

        time_executed = round(time_now - time_start)
        consumption = -1 # consumption in (% / s)
        if sample_counter > 1:
            if median_consumption_last_soc != None:
                tmp_last_soc = median_consumption_last_soc
            else:
                median_consumption_last_soc = state_of_charge
                tmp_last_soc = state_of_charge

            if median_consumption_last_soc_change != None:
                tmp_last_soc_change = median_consumption_last_soc_change
            else:
                median_consumption_last_soc_change = sample_counter
                tmp_last_soc_change = sample_counter

            if tmp_last_soc != state_of_charge:
                tmp_last_soc_change = sample_counter
                median_consumption_last_soc_change = sample_counter
                median_consumption_last_soc = state_of_charge

            consumption = (data_soc[0] - data_soc[tmp_last_soc_change]) / ((tmp_last_soc_change * args.sample_rate) / (60*60))
            consumption = round(consumption, 2)

        if median_consumption_start == 0 and consumption != 0 and consumption != -1:
            median_consumption_start = consumption

        data_median_consumption.append(consumption) # save data

        # print data (to console [and file])
        if sample_counter % (args.output_rate / args.sample_rate) == 0:
            clear_previous_line()
            if args.beautify:
                myPrint(seconds_to_human_form(time_executed), end='\t')
                myPrint(percentage_to_human_form(state_of_charge), end='\t')
                myPrint(seconds_to_human_form(seconds_left), end='\t')
                myPrint(percentage_to_human_form(consumption), '/ h')
            else:
                myPrint(time_executed, end='\t')
                myPrint(state_of_charge, end='\t')
                myPrint(seconds_left, end='\t')
                myPrint(consumption)

        # check if minimum_soc or maximum_soc is reached
        if args.minimum_soc != None and state_of_charge <= args.minimum_soc:
            if args.verbose:
                myPrint('# Batteries state of charge reached the minimum level. Terminating script.')
            end(None, None)
        if args.maximum_soc != None and state_of_charge >= args.maximum_soc:
            if args.verbose:
                myPrint('# Batteries state of charge reached the maximum level. Terminating script.')
            end(None, None)

        sleep(args.sample_rate - (time_now - time_start) % args.sample_rate) # execution time compensation

        sample_counter += 1


def end_error():
    exit(1)

def end(signal_received, frame):
    global time_start
    global time_end
    global battery_soc_start
    global battery_soc_end
    global expected_remaining_time_start
    global expected_remaining_time_end
    global median_consumption_start
    global median_consumption_end

    battery_soc_end = round(psutil.sensors_battery().percent)
    expected_remaining_time_end = round(psutil.sensors_battery().secsleft)
    time_end = time()
    median_consumption_end = round((data_soc[0] - data_soc[-1]) / ((time_end - time_start) / (60*60)), 2)

    # stop all worker threads
    global worker_threads
    for wt in worker_threads:
        wt.terminate()

    # execute min_soc command
    if args.cmd_min_soc != None:
        os.system(args.cmd_min_soc)
    # execute max_soc command
    if args.cmd_max_soc != None:
        os.system(args.cmd_max_soc)
    # execute end command
    if args.cmd_end != None:
        os.system(args.cmd_end)

    if args.beautify:
        # Remove old output
        if system() == 'Linux':
            clear_previous_line()
            clear_previous_line()
            clear_previous_line()
            clear_previous_line()
        else:
            myPrint()
            myPrint()
            myPrint()

        myPrint('# Script started at', strftime("%d.%m.%Y %H:%M:%S", localtime(time_start)), 'with the following values:')
        myPrint()
        myPrint('timeExecuted\tbat %\ttimeRemaining\tconsumption')
        myPrint('hh:mm:ss\t\thh:mm:ss\t(median)')
        myPrint('---------\t-------\t---------\t-----------')
        myPrint(seconds_to_human_form(0), end='\t')
        myPrint(percentage_to_human_form(battery_soc_start), end='\t')
        myPrint(seconds_to_human_form(expected_remaining_time_start), end='\t')
        myPrint(percentage_to_human_form(median_consumption_start), '/ h')

        myPrint()

        myPrint('# Script terminated at', strftime("%d.%m.%Y %H:%M:%S", localtime(time_end)), 'with the following values:')
        myPrint()
        myPrint('timeExecuted\tbat %\ttimeRemaining\tconsumption')
        myPrint('hh:mm:ss\t\thh:mm:ss\t(median)')
        myPrint('---------\t-------\t---------\t-----------')
        myPrint(seconds_to_human_form(round(time_end - time_start)), end='\t')
        myPrint(percentage_to_human_form(battery_soc_end), end='\t')
        myPrint(seconds_to_human_form(expected_remaining_time_end), end='\t')
        myPrint(percentage_to_human_form(median_consumption_end), '/ h')
    else:
        # Remove old output
        if system() == 'Linux':
            clear_previous_line()
            clear_previous_line()
        else:
            myPrint()
            myPrint()
            myPrint()

        myPrint('# script_startet_at', floor(time_start), sep='\t')
        myPrint('# <sec>\t<soc>\t<until>\t<consumption>')
        myPrint(0, end='\t')
        myPrint(battery_soc_start, end='\t')
        myPrint(expected_remaining_time_start, end='\t')
        myPrint(median_consumption_start)

        myPrint()

        myPrint('# script_terminated_at', floor(time_end), sep='\t')
        myPrint('# <sec>\t<soc>\t<until>\t<consumption>')
        myPrint(round(time_end - time_start), end='\t')
        myPrint(battery_soc_end, end='\t')
        myPrint(expected_remaining_time_end, end='\t')
        myPrint(median_consumption_end)

    if args.verbose:
        myPrint('Goodbye!')

    myPrint('', end='')
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, end)
    main()
    end(None, None)
