import logging
import random
import sys

from flask import Flask, json

from datetime import datetime
import sched, time
import sqlite3
import os
from Repository import Repository
from flask import request, Response
from Scenes.AbstractScene import AbstractScene
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Helper.RawHelper import RawHelper
from stravalib import Client

import vesta
from Scenes.Director import Director
import configparser
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
    cur.execute("CREATE TABLE chatgpt_history(id, created_at TEXT DEFAULT CURRENT_TIMESTAMP, role, content)")
    cur.execute("CREATE TABLE scene_instances(id, raw, class_string, start_date, end_date, priority, is_active)")
    Repository().get_connection().commit()

    return Response(response=json.dumps({"status": "initalization done successfully"}), mimetype="application/json")


@app.route('/reset-instances')
def reset_instances():

    cur = Repository().get_connection().cursor()
    cur.execute("delete from scene_instances")
    Repository().get_connection().commit()

    return Response(response=json.dumps({"status": "scene_instances cleared successfully"}), mimetype="application/json")

@app.route('/authorize-strava')
def authorize_strava():
    client = Client()
    url = client.authorization_url(client_id=StravaLastActivityScene.client_id,
                                   redirect_uri='http://127.0.0.1:8000/authorize-strava-callback')

    return Response(response=json.dumps({"status": f"URL: {url}"}), mimetype="application/json")


@app.route('/authorize-strava-callback')
def authorize_strava_callback():

    client = Client()
    code = request.args.get('code')
    token_response = client.exchange_code_for_token(client_id=StravaLastActivityScene.client_id,
                                                    client_secret=StravaLastActivityScene.client_secret,
                                                    code=code)

    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']  # You'll need this in 6 hours
    expires_at = token_response['expires_at']

    config = configparser.ConfigParser()
    config.read('config.ini')

    config['strava']['access_token'] = access_token
    config['strava']['refresh_token'] = refresh_token
    config['strava']['expires_at'] = str(expires_at)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    return Response(response=json.dumps({"status": f"access_token: {access_token} refresh_token: {refresh_token} expires_at: {expires_at}"}), mimetype="application/json")

@app.route('/execute')
def execute():
    candidate = Director().get_next_scene()
    print(f"candidate: {candidate.scene_object.__class__.__name__} (ID: {candidate.id})")
    current = Repository().get_active_scene_instance()
    now = datetime.now()

    # debug
    if current is not None:
        end_date = datetime.strptime(current['end_date'], "%Y-%m-%d %H:%M:%S.%f")
        print(f"now: {now} - end date: {end_date} (Difference: {(end_date-now).total_seconds()})")
    #-

    if current is None:
        print("current is none -> candidate will be executed")
    elif datetime.strptime(current['end_date'], "%Y-%m-%d %H:%M:%S.%f") >= now:
        print(f"current ({current['class_string']}) is still valid (end_date not reached yet)")
        if candidate.priority > current['priority']:
            print("candidate has higher priority than current. Current will be replaced")
            Repository().unmark_active_scene_instance()
        else:
            return Response(response=json.dumps({
                "identifier": current['id'],
                "scene": current['class_string'],
                "message": "candidate has lower or equal priority than current -> keep current",
            }), mimetype="application/json")


    elif datetime.strptime(current['end_date'], "%Y-%m-%d %H:%M:%S.%f") < now:
        print("current is not valid any longer - is_active will be set to false")
        Repository().unmark_active_scene_instance()


    post_execution_candidate = candidate.scene_object.post_execute()
    if post_execution_candidate is not None:
        print("-----------------------------------------> execute post execution candidate!")
        candidate = post_execution_candidate

    print(f"candidate.message: {candidate.message}")
    vesta.pprint(candidate.raw)

    try:
        vboard.write_message(candidate.raw)
    except Exception as exc:
        print(f"HTTP Exception catched")

    Repository().save_scene_instance({
                'id': candidate.id,
                'raw': RawHelper.get_raw_string(candidate.raw),
                'class_string': candidate.scene_object.__class__.__name__,
                'start_date': candidate.start_date,
                'end_date': candidate.end_date,
                'priority': candidate.priority,
                'is_active': True
            })

    return Response(response=json.dumps({
        "identifier": candidate.id,
        "scene": candidate.scene_object.__class__.__name__,
        "message": candidate.message
    }), mimetype="application/json")


@app.route('/storeSnapshot', methods=['POST'])
def store():
    if not "title" in request.json:
        return Response(response=json.dumps({"message": "missing 'title' parameter in request"}), status=400, mimetype="application/json")

    title = request.json['title']
    current_message = vboard.read_message()
    current_message_string = str(current_message).replace(' ', '')

    print("current_message:")
    vesta.pprint(current_message)

    sql = 'INSERT INTO snapshots(title, raw) VALUES(?,?)'
    Repository().get_connection().cursor().execute(sql, (title, current_message_string))
    Repository().get_connection().commit()

    return Response(response=json.dumps({"status": "stored '" + title + "' in database"}), mimetype="application/json")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
