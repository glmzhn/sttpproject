FROM python:3.12-alpine3.19

COPY requirements.txt /temp/requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password service-user

RUN chown -R service-user /app

USER service-user
