from flask import render_template, redirect, flash,  session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, PostForm, InForm
from datetime import datetime
from models import User, ROLE_USER, ROLE_ADMIN, Post
from hashlib import md5
from email.mime.text import MIMEText 
from smtplib import SMTP_SSL as SMTP
from sqlalchemy import update

@app.route('/')
@app.route('/start')
def start():
	return render_template('start.html')


@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
	error = ''
	id_post =  request.args.get('id_post') 
	form = PostForm()
	



	if not (form.nick.data is None):
		to_user = User.query.filter_by(nickname = form.nick.data).first()

		if (form.check.data == False) and not (to_user is None):
			
			if request.form['submit'] == 'send':
				post = Post(body = form.post.data, timestamp = datetime.now(), send_id = g.user.id, get_id = to_user.id, check_in = True, check_out = True, check_draft = False)
				db.session.add(post)
				db.session.commit()
			else: 
				
				
				post = Post(body = form.post.data, timestamp = datetime.now(), send_id = g.user.id, get_id = to_user.id, check_in = False, check_out = False, check_draft = True)
				db.session.add(post)
				db.session.commit()
				
			flash('your message go out')
			return redirect(url_for('index'))
		elif form.nick.data.find('@') > 0:
			try:
				
				SMTPserver = 'smtp.' + form.from_.data[form.from_.data.find('@')+1:]
				print(SMTPserver)
				EMAIL = form.from_.data
				text = form.post.data
				PASSWORD = form.password.data
				subject=""
				recipients = [form.nick.data]
				msg = MIMEText(text, '')
				msg['Subject']= subject
				msg['From']   = EMAIL
				conn = SMTP(SMTPserver)
				conn.set_debuglevel(False)
				conn.login(EMAIL, PASSWORD)
				try:
					conn.sendmail(EMAIL, recipients, msg.as_string())
					print(conn.__doc__)
					flash('your message go out')
				except Exception:
					flash('problem with login or password')
					return redirect(url_for('index'))

				finally:
					conn.quit()
				return redirect(url_for('index'))
			except Exception:
				flash('problem network')
				return redirect(url_for('index'))
				
		else: 
			flash('not correct')
	user = g.user
	posts = []
	if id_post is not None:		
		our_post = Post.query.filter_by(id = id_post).first()
		to_user = User.query.filter_by(id = our_post.get_id).first()
		if our_post.send_id == g.user.id:	
			form.nick.data = to_user.nickname
			form.post.data = our_post.body
	return render_template('index.html', title = 'Home', user = user, posts = posts, form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = InForm()
	if form.validate_on_submit():
		
		user = User.query.filter_by(nickname = form.openid.data).first()
		if not (user is None):
			if user.password == md5(form.openpassword.data).hexdigest():
				login_user(user)
				return redirect(request.args.get('next') or url_for('index'))
	if not (form.openid.data is None) and not (form.openpassword.data is None):
		flash('login or password wrong')
	return render_template('in.html', title = 'Sign In', form = form)
	

		
	
@app.route('/reg', methods = ['GET', 'POST'])
def registr():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login reqest for nickname  = ' + form.openid.data)
		return after_login(form.openid.data, form.openpassword.data, form.openpassword2.data)
	return render_template('login.html', title = 'Log In', form = form)


def after_login(nickname, password, password2):
    user = User.query.filter_by(nickname = nickname).first()
    if nickname is None or nickname == "" or not(user is None):
        flash('Invalid login. Please try again.')
        return redirect(url_for('registr'))
    if password != password2:
	flash('Invalid password')
	return redirect(url_for('registr'))
   
   
    if user is None:
        user = User(nickname = nickname, password = md5(password).hexdigest(), role = ROLE_USER)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Rigth nickname and password, Welcome')
    return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
	g.user = current_user
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('start'))
@app.route('/delete/<idd>')
@login_required
def delete(idd):
	post = Post.query.filter_by(id = idd).first()
	print(idd)
	print(post)
	if post != None:	
		if post.send_id == g.user.id:
			post.check_in = False
			post.check_draft = False
		if post.get_id == g.user.id:
			post.check_out = False
		if not (post.check_in or post.check_out or post.check_draft):
			db.session.delete(post)
	
		db.session.commit()
	return redirect(url_for('user', nickname = g.user.nickname))
@app.route('/update/<idd>')
@login_required
def update(idd):
	post = Post.query.filter_by(id = idd).first()
	p = Post(body = post.body, timestamp = datetime.now(), send_id = post.send_id, get_id = post.get_id, check_in = True, check_out = True, check_draft = False)
	db.session.add(p)
	db.session.commit()
	return redirect(url_for('user', nickname = g.user.nickname))
@app.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user == None:
		flash('User ' + nickname + ' not found')
		return redirect(url_for('user', nickname = g.user.nickname))
	if user != g.user:
		flash("It's not your profile")
		return redirect(url_for('user', nickname = g.user.nickname))
	mes_to = []
	for post in user.mes_to:
		if not (post.check_draft) and post.check_in:
			timestamp = str(post.timestamp)
			timestamp = timestamp[:timestamp.find('.')]
			mes = {'to' : User.query.filter_by(id = post.get_id).first().nickname,
					'from' : user.nickname, 'body'  : post.body, 'timestamp' : post.timestamp,'id' : post.id}
			mes_to.append(mes)
	mes_from = []
	for post in user.mes_from:
		if post.check_out:
		    timestamp = str(post.timestamp)
		    timestamp = timestamp[:timestamp.find('.')]
		    mes = {'from' : User.query.filter_by(id = post.send_id).first().nickname,
					'to' : user.nickname, 'body'  : post.body, 'timestamp' : post.timestamp, 'id' : post.id}
		    mes_from.append(mes)
	mes_draft = []
	for post in user.mes_to:
		if (post.check_draft):
			timestamp = str(post.timestamp)
			timestamp = timestamp[:timestamp.find('.')]
			mes = {'from' : User.query.filter_by(id = post.send_id).first().nickname,
					'to' : user.nickname, 'body'  : post.body, 'timestamp' : post.timestamp,'id' : post.id}
			mes_draft.append(mes)

		
	return render_template('user.html',
	user = user,
	mes_to = mes_to, mes_from = mes_from, mes_draft= mes_draft)

@app.errorhandler(404)
def not_found_error(error):
	flash('Not correct adress') 
	return render_template('base.html'), 404

@app.errorhandler(535)
def not_found_error(error):
	flash('Not correct email or address') 
	return render_template('base.html'), 535
