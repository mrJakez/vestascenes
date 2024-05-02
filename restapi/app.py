import logging
import sys
# import vestaboard # type: ignore
from flask import Flask
import datetime
import sched, time
import sqlite3
import os

import debugpy
debugpy.listen(9000)


app = Flask(__name__)


@app.route('/')
def hello():
	# con = sqlite3.connect("/database/vbcontrol.db")
	# cur = con.cursor()
	# cur.execute("""
    # INSERT INTO movie VALUES
    #     ('Monty Python and the Holy Grail', 1975, 8.2),
    #     ('And Now for Something Completely Different', 1971, 7.5)
	# """)

	print("example how to log towards stdOut")
	return "Hello World!2" + debugpy.__version__



@app.route('/init')
def init():
	if os.path.exists("/database/vbcontrol.db"):
		print("old database existed - removed right now")
		os.remove("/database/vbcontrol.db")

	con = sqlite3.connect("/database/vbcontrol.db")
	cur = con.cursor()
	cur.execute("CREATE TABLE movie(title, year, score)")
	return "init done"


@app.route('/board')
def board():
	# installable = vestaboard.Installable('your_api_key', 'your_api_secret')
	# vboard = vestaboard.Board(installable)
	# vboard.post('Everything you can imagine is real.')
	return "board connector - will come :)"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)