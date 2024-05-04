import logging
import random
import sys
import vestaboard
from flask import Flask, json
import datetime
import sched, time
import sqlite3
import os
from Repository import Repository
from vestaboard.formatter import Formatter
from flask import request, Response

from Scenes.Demo import DemoScene, DemoScene2
from Scenes.SnapshotScene import SnapshotScene

app = Flask(__name__)

installable = vestaboard.Installable('55cea46a-493f-4636-95fe-857094034fca',
                                     'YzFhMTdmOGUtMDhjMS00ZTNhLWFiOTktYjMxYTU4ZjEyYWQ1')
vboard = vestaboard.Board(installable)
vboardRead = vestaboard.Board(apiKey='6a27cdd6+cc6f+4ad9+9631+5910d42102ce', readWrite=True)


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
    return "Neuer test Hello World!2"


@app.route('/init')
def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    Repository._connection = None
    cur = Repository().get_connection().cursor()
    cur.execute("CREATE TABLE snapshots(title, raw)")
    return "init done"


@app.route('/board')
def board():
    vboard.post('Everything you can imagine is real.')
    return "board connector - will come for sure :)"


@app.route('/update')
def update():
    # check if some event was triggered meanwhile. If yes display them, otherwise random content

    # random content
    ScenesArray = []  # empty array

#    ScenesArray.append(DemoScene())
#    ScenesArray.append(DemoScene2())
    ScenesArray.append(SnapshotScene())

    current_scene = random.choice(ScenesArray)
    raw_text = current_scene.get_raw()

    print(raw_text)
    vboard.raw(raw_text, pad='center')
    return "updated from " + current_scene.__class__.__name__


@app.route('/snapshot', methods=['POST'])
def store():
    if not "title" in request.json:
        return Response(response=json.dumps({"message": "missing 'title' parameter in request"}), status=400)

    title = request.json['title']
    raw = vboardRead.read()

    print("raw:" + str(raw))
    print("raw string:" + str(raw['currentMessage']['layout']))

    sql = 'INSERT INTO snapshots(title, raw) VALUES(?,?)'
    Repository().get_connection().cursor().execute(sql, (title, str(raw['currentMessage']['layout'])))
    Repository().get_connection().commit()

    return Response(response=json.dumps({"status": "stored '" + title + "' in database"}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
