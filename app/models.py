
from sqlalchemy import event, DDL
from flask.ext.login import UserMixin
from app import db, lm

ROLE_USER = 0
ROLE_ADMIN = 1

@lm.user_loader
def get_user(ident):
  return User.query.get(int(ident))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), index = True, unique = True)
	password = db.Column(db.String(120))
	role = db.Column(db.SmallInteger , default = ROLE_USER)
	mes_from = db.relationship("Post", primaryjoin="Post.get_id==User.id")
	mes_to = db.relationship("Post", primaryjoin="Post.send_id==User.id")
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	send_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	get_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	check_in = db.Column(db.Boolean)
	check_out = db.Column(db.Boolean)
	check_draft = db.Column(db.Boolean)	

	def __repr__(self):
		return '<Post %r>' %(self.body)


