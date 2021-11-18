import psutil
import time

print('<seconds since start>\t<battery percent>\t<seconds left>')
time_start = time.time()
while True:
    battery = psutil.sensors_battery()
    print(time.time() - time_start, battery.percent, battery.secsleft, sep='\t')
    time.sleep(60)
