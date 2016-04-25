from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(Form):
    openid = TextField('openid', validators = [DataRequired()])
    openpassword = PasswordField('password', validators = [DataRequired()])
    openpassword2 = PasswordField('password', validators = [DataRequired()])
class InForm(Form):
    openid = TextField('openid', validators = [DataRequired()])
    openpassword = PasswordField('password', validators = [DataRequired()])
    remember_me = BooleanField('remember_me', default = False)
class PostForm(Form):
	post = TextAreaField('post', validators = [DataRequired()])
	nick = TextField('nick', validators = [DataRequired()])
	check = BooleanField('check', default = False)
	password = TextField('password', validators = [DataRequired()])
	from_ = TextField('from_', validators = [DataRequired()])
