from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.search import add_to_index,remove_from_index,query_index










# class SearchableMixin(object):
#     @classmethod
#     def search(cls, expression, page, per_page):
#         ids, total = query_index(cls.__tablename__, expression, page, per_page)
#         if total == 0:
#             return cls.query.filter_by(id=0), 0
#         when = []
#         for i in range(len(ids)):
#             when.append((ids[i], i))
#         return cls.query.filter(cls.id.in_(ids)).order_by(
#             db.case(when, value=cls.id)), total

#     @classmethod
#     def before_commit(cls, session):
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }

#     @classmethod
#     def after_commit(cls, session):
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.__tablename__, obj)
#         session._changes = None

#     @classmethod
#     def reindex(cls):
#         for obj in cls.query:
#             add_to_index(cls.__tablename__, obj)

# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)











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

