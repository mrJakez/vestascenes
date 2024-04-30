import logging
import sys
import sched, time


print("runner started")


while True:
	# Hier kommt der Code für deinen Prozess
	# Zum Beispiel:
	print("Der Runner läuft weiter...")
		
	# Pausiere für eine gewisse Zeit, um die CPU-Last zu reduzieren
	time.sleep(5)  # Pausiere für 5 Sekunden