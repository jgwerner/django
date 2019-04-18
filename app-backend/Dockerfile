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

RUN addgroup -g 1000 -S app && \
    adduser -u 1000 -S app -G app

RUN mkdir -p /srv/
WORKDIR /srv/
RUN virtualenv env --python=python3
RUN . env/bin/activate; pip install --upgrade setuptools pip wheel

WORKDIR /srv/app/

ADD requirements/ /srv/app/requirements

# install requirements to run app
RUN . ../env/bin/activate; pip install -r requirements/base.txt

ADD . /srv/app

RUN touch /srv/app/celerybeat.pid
RUN chown -R 1000:1000 /srv/
USER app

ENTRYPOINT ["/srv/app/docker-entrypoint.sh"]

EXPOSE 80