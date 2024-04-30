import logging
import sys
# import vestaboard # type: ignore
from flask import Flask
import datetime
import sched, time

app = Flask(__name__)

@app.route('/')
def hello():
	print("example how to log towards stdOut")
	return "Hello World!"


@app.route('/board')
def board():
	# installable = vestaboard.Installable('your_api_key', 'your_api_secret')
	# vboard = vestaboard.Board(installable)
	# vboard.post('Everything you can imagine is real.')
	return "board connector - will come :)"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)