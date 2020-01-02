import os


class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'this-is-a-secret-key'
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI') or 'postgresql://docker:docker@localhost/slackpro'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    ELASTICSEARCH_URL=os.environ.get('ELASTICSEARCH_URL') or 'localhost:9200'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
