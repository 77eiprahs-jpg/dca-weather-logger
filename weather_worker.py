import time
from weather_collector import collect

while True:
    collect()
    time.sleep(1800)  # every 30 minutes
