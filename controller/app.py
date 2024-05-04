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
from Scenes.AbstractScene import DemoAbstractScene
from Scenes.SnapshotScene import SnapshotScene
from Scenes.ChatGPTScene import ChatGPTScene

app = Flask(__name__)

installable = vestaboard.Installable('55cea46a-493f-4636-95fe-857094034fca','YzFhMTdmOGUtMDhjMS00ZTNhLWFiOTktYjMxYTU4ZjEyYWQ1')
vboard = vestaboard.Board(installable)

vboardRead = vestaboard.Board(apiKey='6a27cdd6+cc6f+4ad9+9631+5910d42102ce', readWrite=True)

@app.route('/')
def hello():
    return "welcome to vestaboard_control"


@app.route('/init')
def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    Repository._connection = None
    cur = Repository().get_connection().cursor()
    cur.execute("CREATE TABLE snapshots(title, raw)")
    return Response(response=json.dumps({"status": "initalization done successfully"}))


@app.route('/update')
def update():
    # check if some event was triggered meanwhile. If yes display them, otherwise random content
    # TODO

    # random content
    ScenesArray = []  # empty array

#    ScenesArray.append(DemoScene())
#    ScenesArray.append(SnapshotScene())
    ScenesArray.append(ChatGPTScene())

    current_scene = random.choice(ScenesArray)
    current_scene.execute(vboard)

    return Response(response=json.dumps({"status": "updated from " + current_scene.__class__.__name__}))


@app.route('/storeSnapshot', methods=['POST'])
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
