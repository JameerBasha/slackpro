from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy  import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_socketio import SocketIO, send
from elasticsearch import Elasticsearch
from celery import Celery
import arrow



db=SQLAlchemy()
login=LoginManager()
moment=Moment()
socketio=SocketIO()


# def create_app(config_class=Config):

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate=Migrate()
login.init_app(app)
login.login_view='auth.login'
migrate.init_app(app,db)
moment.init_app(app)


celery=Celery(app.name,broker='redis://localhost:6379',backend='redis://localhost:6379')
celery.conf.update(app.config)



elasticsearch=Elasticsearch([app.config['ELASTICSEARCH_URL']])\
	if app.config['ELASTICSEARCH_URL'] else None
if not(elasticsearch.ping()):
	elasticsearch=None

socketio.init_app(app)


from app.auth import bp as auth_bp
app.register_blueprint(auth_bp)

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.dashboard import bp as dashboard_bp
app.register_blueprint(dashboard_bp)


if __name__ == '__main__':
	pass



from app import models


# run with  gunicorn -k gevent -w 1 slackpro:app
