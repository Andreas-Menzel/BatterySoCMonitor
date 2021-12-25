# BatterySoCMonitor
Simple Python script that monitors the batteries state of charge.

## Examples

### Just monitor the batteries state of charge
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
```
python BatterySoCMonitor.py --sample_rate 60 -v -b
```

### Monitor with CPU load
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
- save results in log file (`battery_soc.log`)
- create 4 threads with 100% CPU-usage
```
python BatterySoCMonitor.py --sample_rate 60 -v -b --log_file battery_soc.log --workers cpuLoad cpuLoad cpuLoad cpuLoad
```

### Overnight test
- monitor the batteries state of charge at 1 minute intervals
- display all information in human readable form
- save results in log file (`battery_soc.log`)
- terminate script and shutdown system at 10%
```
python BatterySoCMonitor.py --sample_rate 60 -v -b --log_file battery_soc.log --minimum_soc 10 --cmd_min_soc 'shutdown now'
```
