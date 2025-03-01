# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /Users/medhansh/Club Tasks/DVM Task/BUS_DJANGO/django_project

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# Expose the port Django runs on
EXPOSE 8000
