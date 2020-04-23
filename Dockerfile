FROM python:3.7
MAINTAINER Kantai <kantai.developer@gmail.com>

WORKDIR /discord_bot
COPY . /discord_bot

RUN pip install --no-cache-dir -r requirements.txt

CMD python index.py