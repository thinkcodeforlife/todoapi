FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /todoapp

WORKDIR /todoapp

ADD . /todoapp

RUN pip install -r requirements.txt

