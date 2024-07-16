FROM python:3-alpine

WORKDIR /app

RUN mkdir /db # Create db folder

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD python main.py
