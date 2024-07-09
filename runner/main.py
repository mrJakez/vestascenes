import sys
import time

print("runner started. Python version: " + sys.version)
time.sleep(5)  # pause for 5 seconds - to provide time for the controller to boot up
while True:
    print("runner executed....")
    r = requests.get("http://api:8200/execute")
    #print(r.text)

    time.sleep(15)  # pause for 15 seconds
