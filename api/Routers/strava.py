from fastapi import APIRouter, Request
# from fastapi import FastAPI, Request
from stravalib import Client

from Scenes.StravaLastActivityScene import StravaLastActivityScene

router = APIRouter()


@router.get("/authorize-strava", tags=["strava-oauth"], description="Initializes the strava connection. Returns an "
                                                                    "authorization link which will trigger the callback url afterwards.")
async def authorize_strava(request: Request):
    client = Client()

    redirect_url = f'http://{request.url.hostname}:{request.url.port}/authorize-strava-callback'

    if request.url.port is None or request.url.port == 80:
        redirect_url = f"http://{request.url.hostname}/authorize-strava-callback"

    url = client.authorization_url(client_id=StravaLastActivityScene.client_id,
                                   redirect_uri=redirect_url)

    return {"initialized": f"{StravaLastActivityScene.is_initialized()}", "url": url}


@router.get("/authorize-strava-callback", tags=["strava-oauth"], description="Callback which is triggered by the "
                                                                             "strava authorization process. Within a success case the access and refresh tokens are provided and stored in a local configuration.")
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
