import logging
import sys
# import vestaboard # type: ignore
from flask import Flask
#from flask_apscheduler import APScheduler
import datetime
import sched, time

print("--------------->>>>>>>>>>> am start")

app = Flask(__name__)

@app.route('/')
def hello():
	print("example how to log towards stdOut")
	return "Hello World!NEU"


@app.route('/board')
def hello2():

	# installable = vestaboard.Installable('your_api_key', 'your_api_secret')
	# vboard = vestaboard.Board(installable)
	# vboard.post('Everything you can imagine is real.')

	return "AAA foobar"

print("--------------->>>>>>>>>>> am start 2")


#function executed by scheduled job
def my_job(text):
    print(text, str(datetime.datetime.now()))


print("--------------->>>>>>>>>>> am start 3")



app.run(host='0.0.0.0', port=8000)
if __name__ == '__main__':
	print("--------------->>>>>>>>>>> within __main__")

	app.run(host='0.0.0.0', port=8000)
	print("--------------->>>>>>>>>>> am start 4")
	while True:
		# Hier kommt der Code für deinen Prozess
		# Zum Beispiel:
		print("Der Prozess läuft weiter...")
		
		# Pausiere für eine gewisse Zeit, um die CPU-Last zu reduzieren
		time.sleep(5)  # Pausiere für 5 Sekunden




	print("--------------->>>>>>>>>>> am start END")
