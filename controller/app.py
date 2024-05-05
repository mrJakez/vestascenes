import logging
import random
import sys

from flask import Flask, json
import datetime
import sched, time
import sqlite3
import os
from Repository import Repository
from flask import request, Response
from Scenes.AbstractScene import DemoScene
from Scenes.SnapshotScene import SnapshotScene
from Scenes.ChatGPTScene import ChatGPTScene
import vesta

vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")
app = Flask(__name__)


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

    #ScenesArray.append(DemoScene())
    ScenesArray.append(SnapshotScene())
    #ScenesArray.append(ChatGPTScene())

    current_scene = random.choice(ScenesArray)
    current_scene.execute(vboard)

    return Response(response=json.dumps({
        "scene": current_scene.__class__.__name__,
        "message": current_scene.lastGeneratedMessage
    }))


@app.route('/storeSnapshot', methods=['POST'])
def store():
    if not "title" in request.json:
        return Response(response=json.dumps({"message": "missing 'title' parameter in request"}), status=400)

    title = request.json['title']
    current_message = vboard.read_message()
    current_message_string = str(current_message).replace(' ', '')

    print("current_message:")
    vesta.pprint(current_message)

    sql = 'INSERT INTO snapshots(title, raw) VALUES(?,?)'
    Repository().get_connection().cursor().execute(sql, (title, current_message_string))
    Repository().get_connection().commit()

    return Response(response=json.dumps({"status": "stored '" + title + "' in database"}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
