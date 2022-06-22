# BatterySoCMonitor - Evaluate your batteries health!

## Monitor the batteries state of charge and approximate the total battery capacity in hours.

BatterySoCMonitor is a python script to test your systems battery and monitor
the remaining state of charge (soc). The script includes features to execute
commands (e.g. system shutdown) when a specified soc is reached. You can start
workers to test the battery under cpu-load. It can create log files in a
unified, script-friendly format as well as in a more human readable form.

## How can I use BatterySoCMonitor?

The following examples should explain how the script works.

**Just monitor the batteries state of charge**
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
```
python BatterySoCMonitor.py --sample_rate 60 -v -b
```

**Monitor with CPU load**
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
- save results in log file (`battery_soc.log`)
- create 4 threads with 100% CPU-usage
```
python BatterySoCMonitor.py --sample_rate 60 -v -b --log_file battery_soc.log --workers cpuLoad cpuLoad cpuLoad cpuLoad
```

**Overnight test**
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
- save results in log file (`battery_soc.log`)
- terminate script and shutdown system at 10%
```
python BatterySoCMonitor.py --sample_rate 60 -v -b --log_file battery_soc.log --minimum_soc 10 --cmd_min_soc 'shutdown now'
```

### Parameters

```
usage: BatterySoCMonitor [-h] [--version] [--sample_rate] [--output_rate] [-v] [-b] [-l ] [--minimum_soc] [--maximum_soc] [--cmd_min_soc] [--cmd_max_soc] [--cmd_start] [--cmd_end] [-w {cpuLoad} [{cpuLoad} ...]]

Monitor the batteries state of charge and approximate the total battery capacity in hours.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --sample_rate         Delay (in seconds) between each measurement. Must be a divisor of --output_rate
  --output_rate         Delay (in seconds) between each data output. Must be a multiple of --sample_rate
  -v, --verbose         Print more information
  -b, --beautify        Print information in human readable form
  -l [], --log_file []  Filename of the log-file
  --minimum_soc         Terminate script when batteries state of charge is below or equal to this percentage
  --maximum_soc         Terminate script when batteries state of charge is above or equal to this percentage
  --cmd_min_soc         Command that will be executed when the script terminates because of the batteries state of charge (see --minimum_soc)
  --cmd_max_soc         Command that will be executed when the script terminates because of the batteries state of charge (see --maximum_soc)
  --cmd_start           Command that will be executed when the script starts
  --cmd_end             Command that will be executed when the script terminates
  -w {cpuLoad} [{cpuLoad} ...], --workers {cpuLoad} [{cpuLoad} ...]
                        Specify a list of worker jobs. Each worker creates a new process
```


## See BatterySoCMonitor in action

I used this script to test and monitor the battery of my *Lenovo Yoga 530-14IKB*.
The test results (log files) before and after changing the battery can be found
in `demo-log-files/`.

Check the first few lines to see the script version and parameters that were
used. The last few lines can tell you how long the battery did last.

Have a look at `demo-log-files/Lenovo-Yoga-530-oldBatt-Fedora_8x_cpuLoad_-_1.txt`
vs. `demo-log-files/Lenovo-Yoga-530-newBatt_8x_CpuLoad_-_1.txt`. These tests
show that the old battery was not able to power the laptop when in heavy use.


## Limitations

- **Lower resolution on Windows**

    On Windows the remaining batteries state of charge is returned as an integer
    number. Decreasing the sample rate below a certain threshold will not result
    in a better resolution. (On Linux systems the batteries state of charge is
    rounded to two decimal places.)
