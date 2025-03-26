FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY Helper/* Helper/
COPY Models/* Models/
COPY Scenes/* Scenes/
COPY Routers/* Routers/
COPY *.py ./
COPY settings.ini ./
COPY git-version.txt ./
COPY Initial-snapshots/* Initial-snapshots/

CMD uvicorn main:app --host 0.0.0.0 --port 80