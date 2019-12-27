from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.search import add_to_index,remove_from_index,query_index


class UserTable(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(50), index=True, unique=True)
    email=db.Column(db.String(50), index=True, unique=True)
    password_hash=db.Column(db.String(128))
    __searchable__=['username']

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<UserTable {}>'.format(self.username)

class GroupTable(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    groupname=db.Column(db.String(50),index=True)
    admin_id=db.Column(db.Integer,db.ForeignKey('user_table.id'))
    group_description=db.Column(db.String(150), index=True)
    __searchable__=['groupname']


class GroupMembers(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    group_id=db.Column(db.Integer, db.ForeignKey('group_table.id'))
    member_id=db.Column(db.Integer, db.ForeignKey('user_table.id'))
    member_name=db.Column(db.String(50),  db.ForeignKey('user_table.username'))


class Message(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    group_id=db.Column(db.Integer, db.ForeignKey('group_table.id'))
    user_id=db.Column(db.Integer, db.ForeignKey('user_table.id'))
    user_name=db.Column(db.String(50), db.ForeignKey('user_table.username'))
    message=db.Column(db.String(500))
    message_time=db.Column(db.DateTime, default=datetime.utcnow)
    __searchable__=['message']

@login.user_loader
def load_user(id):
    return UserTable.query.get(int(id))

from app.search import add_to_index, remove_from_index, query_index

