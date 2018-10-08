FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y \
        gcc \
        nginx
WORKDIR /code/
ADD requirements.txt /code/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /code/

WORKDIR /code/iticket

EXPOSE 8080