from app import db
from flask_login import current_user

def db_committer(obj):
	db.session.add(obj)
	db.session.commit()
	return True

def is_authenticated():
	if(current_user.is_authenticated):
		return True
	else:
		return False