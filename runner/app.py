import sys
import time
import requests

print("runner started. Pyhton version: " + sys.version)

while True:
	# Hier kommt der Code für deinen Prozess
	# Zum Beispiel:
	print("runner executed....")
	r = requests.get("http://restapi:8000/")
	#print(r.text)
		
	# Pausiere für eine gewisse Zeit, um die CPU-Last zu reduzieren
	time.sleep(5)  # Pausiere für 5 Sekunden