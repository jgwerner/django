FROM python:3.6-alpine

RUN apk update \
 && apk upgrade \
 && apk add --no-cache \
    build-base \
    git \
    postgresql-dev \
    libffi-dev \
    zlib-dev \
    libjpeg \
    jpeg-dev \
    curl

RUN pip install virtualenv
    
RUN mkdir -p /workspaces/
RUN mkdir -p /srv/app/staticfiles

WORKDIR /srv/
RUN virtualenv env --python=python3
RUN . env/bin/activate; pip install --upgrade setuptools pip wheel

ADD requirements/ /srv/app/requirements

# install requirements to run app
RUN . env/bin/activate; pip install -r app/requirements/base.txt

ADD . /srv/app

RUN touch /srv/app/celerybeat.pid

RUN addgroup -g 1000 -S app && \
    adduser -u 1000 -S app -G app
RUN chown -R 1000:1000 /srv/
RUN chown -R 1000:1000 /workspaces/

USER app
WORKDIR /srv/app

ENTRYPOINT ["/srv/app/docker-entrypoint.sh"]

EXPOSE 8080