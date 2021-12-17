FROM python:3.8

COPY requirements.txt /

RUN apt-get update \
 && apt-get install -y \
 wget \
 python3-dev \
 graphviz \
 libgraphviz-dev \
 pkg-config

RUN pip3 install -r requirements.txt && pip3 install gunicorn

ARG HASURA_GRAPHQL_ADMIN_SECRET
ARG HASURA_GRAPHQL_API
ARG SECRET_KEY
ARG FLASK_ENV
ARG CLIENT_HASURA_GRAPHQL_API

WORKDIR flask
ADD . /flask/


CMD [ "gunicorn", "--workers=4", "--threads=1", "-b 0.0.0.0:8050", "atlas:server"]
