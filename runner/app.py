import sys
import time
import requests

print("runner started. Python version: " + sys.version)

while True:
    print("runner executed....")
    r = requests.get("http://controller:8000/")
    #print(r.text)

    time.sleep(15)  # pause for 15 seconds
