FROM ubuntu

RUN apt-get update

RUN apt install python3 -y
RUN apt install python3-venv -y -y

RUN apt install libpq-dev python3-dev -y python3-virtualenv

RUN apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0.0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y

RUN apt install gcc musl-dev -y 

COPY ./requirements.txt /

RUN python3 -m venv venv
#RUN python3 -m virtualenv --python=/usr/bin/python3 /venv
RUN /venv/bin/pip3 install psycopg2-binary
RUN /venv/bin/pip3 install -r requirements.txt


EXPOSE 8000

ADD . /slackpro
RUN chmod +x /slackpro/boot.sh
CMD ["/slackpro/boot.sh"]
