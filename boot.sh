#!/bin/bash
source venv/bin/activate
echo abcdefghijklmnopqrstuvwxyz
python3 /slackpro/dbcreate.py

/venv/bin/gunicorn -k eventlet --workers 1 -b 0.0.0.0:8000 --chdir /slackpro wsgi:app
/venv/bin/celery -A /slackpro/app.celery
