
FROM ubuntu:xenial

MAINTAINER Curtis Lassam <curtis@lassam.net>

RUN apt-get update && apt-get install -y python3 python3-pip python3-setuptools python3-dev \
                                         git curl build-essential gcc \
                                         postgresql-client libpq-dev python3-dev\
                                         libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
                                         libwebp-dev tcl8.5-dev tk8.5-dev
ADD requirements.txt /usr/local/requirements.txt
RUN pip3 install -r /usr/local/requirements.txt

EXPOSE 8080
