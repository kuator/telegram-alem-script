FROM python:3.9.13-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN 
RUN apt-get update && apt-get install -y --no-install-recommends libmagic1

COPY requirements.txt requirements.txt


RUN pip install --upgrade pip \
    && pip install --no-cache-dir -Ur requirements.txt

COPY . /app
