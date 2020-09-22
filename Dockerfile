# pull official base image
FROM python:latest

# set work directory
RUN mkdir /usr/src/powerdash
WORKDIR /usr/src/powerdash

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libffi-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/powerdash/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/powerdash/