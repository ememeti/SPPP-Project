from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model) :
  id = db.Column(db.Integer, primary_key=True)
  fullname = db.Column(db.String(80), index=True)
  username = db.Column(db.String(16), index=True, unique=True)
  passhash = db.Column(db.String(128))
  authen = db.Column(db.Boolean())
  joingroups = db.Column(db.Boolean())

  def __repr__(self) :
    return '{}'.format(self.username)

  def __init__(self, **kwargs):
    super(User, self).__init__(**kwargs)

  def set_pswrd(self, pswrd) :
    self.passhash = generate_password_hash(pswrd)

  def check_pswrd(self, pswrd) :
    return check_password_hash(self.passhash, pswrd)

  def set_authen(self, val) :
    self.authen = val

  def set_groupauthen(self, val) :
    self.joingroups = val

class Group(db.Model) :
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(10), index=True, unique=True) 

  def __repr__(self) :
    return '<Group {}>'.format(self.name)

class Item(db.Model) :
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(68), index=True, unique=True)
  fname = db.Column(db.String(68), index=True) 
  metatype=db.Column(db.String(10), index=True)
  metasize=db.Column(db.Integer)
  author_user = db.Column(db.String(16), db.ForeignKey('user.username')) # links User.username to author_user to pull creator name
  descriptor = db.Column(db.String(1000), index=True)
  creation = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  lastaccess = db.Column(db.DateTime, index=True, default=datetime.utcnow) 
  group_name = db.Column(db.String(10), db.ForeignKey('group.name')) # links Group.name to group_name to pull group name

  def __repr__(self) :
    return '<Item {}>'.format(self.file)

class Members(db.Model) :
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(16), db.ForeignKey('user.username')) # links User.username to members
  groupname = db.Column(db.String(10), db.ForeignKey('group.name')) # links Group.id to group_id to pull group name

  def __repr__(self) :
    return '<Group {}>'.format(self.groupname)


@login.user_loader
def load_user(id) :
  return User.query.get(int(id))

  
