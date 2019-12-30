chmod 400 deploy.pem
ssh -i "deploy.pem" ubuntu@ec2-13-127-243-209.ap-south-1.compute.amazonaws.com
yes
sudo apt update 
sudo apt install postgresql
y
sudo -i -u postgres
psql
create role ubuntu with login superuser;
\q
exit
createdb slackpro
git clone http://gitlab.com/jameerbasha/slackpro
sudo apt install redis
y
cd slackpro
nano requirements.txt 'remove pkg resources package'
CTRL+S
CTRL+X
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
sudo apt install libpq-dev python3-dev
y
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

y

pip3 install -r requirements.txt

rm -rf migrations

flask db init
flask db migrate
flask db upgrade



cd /etc/systemd/system
sudo touch slackpro.service
sudo nano slackpro.service
"
[Unit]
Description=Gunicorn instance to serve slackpro
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/slackpro
Environment="PATH=/home/ubuntu/slackpro/venv/bin"
ExecStart=/home/ubuntu/slackpro/venv/bin/gunicorn -k eventlet  --workers 1 --bind unix:slackpro.sock -m 007 wsgi:app
StandardOutput=append:/var/log/slackpro/access.log
StandardError=append:/var/log/slackpro/service.log


[Install]
WantedBy=multi-user.target
"
CTRL + S
CTRL + X

sudo systemctl daemon-reload
sudo systemctl start slackpro

sudo apt install nginx
y

cd /etc/nginx/sites-enabled
sudo touch slackpro
sudo nano slackpro

"

server{
        listen 80;
        server_name 13.127.243.209;
        location / {
                proxy_redirect off;
                proxy_set_header Host $http_host;
                proxy_pass http://unix:/home/ubuntu/slackpro/slackpro.sock;
        }
}
"

CTRL + S
CTRL + X

sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

Go to aws amazon and enable security groups with port 80

cd /etc/default
sudo touch celeryd
sudo nano celeryd

"
CELERYD_NODES="worker1"

CELERY_APP="app.celery"

CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

CELERYD_LOG_LEVEL=INFO

# Path to celery binary, that is in your virtual environment
CELERY_BIN=/home/ubuntu/slackpro/venv/bin/celery

CELERYBEAT_PID_FILE="/var/run/celery/beat.pid"
CELERYBEAT_LOG_FILE="/var/log/celery/beat.log"

"
CTRL + S
CTRL + X

cd /etc/systemd/system
sudo touch celeryd.service

"
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=ubuntu
EnvironmentFile=/etc/default/celeryd
WorkingDirectory=/home/ubuntu/slackpro
ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
  -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
  --pidfile=${CELERYD_PID_FILE}'
ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
  -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'

[Install]
WantedBy=multi-user.target
"
CTRL + S
CTRL + X

sudo touch celerybeat.service
sudo nano celerybeat.service

"
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
EnvironmentFile=/etc/default/celeryd
WorkingDirectory=/home/ubuntu/slackpro
ExecStart=/bin/sh -c '${CELERY_BIN} beat  \
  -A ${CELERY_APP} --pidfile=${CELERYBEAT_PID_FILE} \
  --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL}'

[Install]
WantedBy=multi-user.target
"
CTRL + S
CTRL + X


sudo mkdir /var/log/celery /var/run/celery
sudo chown ubuntu:ubuntu /var/log/celery /var/run/celery

sudo systemctl daemon-reload

sudo systemctl enable celeryd
sudo systemctl enable celerybeat


sudo systemctl start celeryd
sudo systemctl start celerybeat

cd /home/ubuntu/slackpro


