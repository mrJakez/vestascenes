import os
from fastapi import FastAPI
import vesta
from datetime import datetime

from Repository import Repository
from stravalib import Client

from Scenes.Director import Director
from Scenes.StravaLastActivityScene import StravaLastActivityScene
from Helper.RawHelper import RawHelper


#test
from openai import OpenAI


app = FastAPI()
vboard = vesta.ReadWriteClient("3e5dc670+a418+43f0+acd5+4ff8cc5fb2fd")


@app.get("/")
async def root():
    foo = 666
    return {"message": "welcome to vesta_control"}


@app.get("/init/")
async def init():
    if os.path.exists("/database/vbcontrol.db"):
        print("old database existed - removed right now")
        os.remove("/database/vbcontrol.db")

    Repository._connection = None
    cur = Repository().get_connection().cursor()
    cur.execute("CREATE TABLE snapshots(title, raw)")
    cur.execute("CREATE TABLE chatgpt_history(id, created_at TEXT DEFAULT CURRENT_TIMESTAMP, role, content)")
    cur.execute("CREATE TABLE scene_instances(id, raw, class_string, start_date, end_date, priority, is_active)")
    Repository().get_connection().commit()
    return {"status": "initalization done successfully"}


@app.get("/execute")
async def execute():
    #return {"disabled":"true"}
    candidate = Director().get_next_scene()
    print(f"candidate: {candidate.scene_object.__class__.__name__} (ID: {candidate.id})")
    current = Repository().get_active_scene_instance()
    now = datetime.now()

    # debug
    if current is not None:
        end_date = datetime.strptime(current['end_date'], "%Y-%m-%d %H:%M:%S.%f")
        print(f"now: {now} - end date: {end_date} (Difference: {(end_date - now).total_seconds()})")
    #-

    if current is None:
        print("current is none -> candidate will be executed")
    elif datetime.strptime(current['end_date'], "%Y-%m-%d %H:%M:%S.%f") >= now:
        print(f"current ({current['class_string']}) is still valid (end_date not reached yet)")
        if candidate.priority > current['priority']:
            print("candidate has higher priority than current. Current will be replaced")
            Repository().unmark_active_scene_instance()
        else:
            return {
                "identifier": current['id'],
                "scene": current['class_string'],
                "message": "candidate has lower or equal priority than current -> keep current",
            }


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

    return {
        "identifier": candidate.id,
        "scene": candidate.scene_object.__class__.__name__,
        "message": candidate.message
    }


@app.get("/reset-instances")
async def reset_instances():
    cur = Repository().get_connection().cursor()
    cur.execute("delete from scene_instances")
    Repository().get_connection().commit()
    return {"message": "scene_instances cleared successfully"}


@app.get("/authorize-strava")
async def authorize_strava():
    client = Client()
    url = client.authorization_url(client_id=StravaLastActivityScene.client_id,
                                   redirect_uri='http://127.0.0.1:8000/authorize-strava-callback')

    return {"status": f"URL: {url}"}


@app.get("/authorize-strava-callback")
async def authorize_strava_callback(code: str):
    client = Client()

    token_response = client.exchange_code_for_token(client_id=StravaLastActivityScene.client_id,
                                                    client_secret=StravaLastActivityScene.client_secret,
                                                    code=code)

    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']  # You'll need this in 6 hours
    expires_at = token_response['expires_at']

    StravaLastActivityScene.store_tokens(access_token, refresh_token, expires_at)
    return {"status": f"access_token: {access_token} refresh_token: {refresh_token} expires_at: {expires_at}"}


@app.get("/hellofuck/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
