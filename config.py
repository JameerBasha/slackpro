import os


class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'this-is-a-secret-key'
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI') or 'postgresql:///slackpro'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    ELASTICSEARCH_URL=os.environ.get('ELASTICSEARCH_URL') or 'localhost:9200'