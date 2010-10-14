#!/ usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort, jsonify

from flaskext.couchdb import CouchDBManager, ViewDefinition
from flaskext.openid import OpenID
from datetime import datetime
from uuid import uuid1

app = Flask(__name__)
app.config.update(
    COUCHDB_SERVER = 'http://localhost:5984/',
    COUCHDB_DATABASE = 'brain',
    SECRET_KEY = '\xb8n\x9c\xe2&]\x85\x1e\xf1\xf2\x938\xe4SA\xc5\x08\xcf\x00\x92\xf5\x7f\xbe\xc8',
    DEBUG = True
)

# CouchDB
manager = CouchDBManager(auto_sync=False)
all_users_view = ViewDefinition('users', 'all', '''\
    function (doc) {
        if (doc.type == 'user') {
            emit(doc.openid, null)
        };
    }''')
all_text_view = ViewDefinition('text', 'all', '''\
    function (doc) {
        if (doc.type != 'user') {
            emit(doc.date, {title: doc.title, content: doc.content, user: doc.user})
        };
    }''')
manager.add_viewdef((all_users_view, all_text_view))
manager.setup(app)
manager.sync(app)

# setup flask-openid
oid = OpenID(app)

#----------------------------------------#
def get_date():
    #return datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')
    return datetime.utcnow()
    
@app.before_request
def before_request():
    g.user = None
    if 'nickname' in session:
	#doc = all_users_view[session['openid']]
	#if doc.total_rows > 0:		# mindestens ein Eintrag gefunden
	#    g.user = doc.rows[0]
	# ToDo fehler bei mehreren Treffern 
	g.user = session

@app.route('/')
def index():
    #return jsonify(g.user)
    texts = all_text_view()
    for row in texts.rows :
      row['value']['content'] = row['value']['content'][:60]
	#return jsonify(texts.rows)
    return render_template('index.html', texts=texts.rows)
    
@app.route('/auth/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'GET':
        openid = request.args.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    doc = all_users_view[session['openid']]
    if doc.total_rows > 0:
	user = doc.rows[0]
	session['nickname'] = user['id']
        flash(u'Successfully signed in')
        #g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname, nickname=resp.nickname,
                            email=resp.email))


@app.route('/user/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        nickname = request.form['nickname']
        if not name:
            flash(u'Error: you have to provide a name')
        elif not nickname:
	    flash(u'Error: you have to provide a nickname')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
	    document = dict(openid=session['openid'], type='user', name=name, email=email, date=get_date(), active='true')
	    g.couch[nickname] = document
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/user/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        return redirect(url_for('login'))
    user = g.couch[g.user['nickname']]
    form = dict(name=user['name'], email=user['email'], nickname=user['_id'])
    if request.method == 'POST':
        if 'delete' in request.form:
            g.couch.delete(g.user)
            session.pop('openid', None)
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        form['nickname'] = request.form['nickname']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif not form['nickname']:
	    flash(u'Error: you have to provide a nickname')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully changed')
            user['name'] = form['name']
            user['email'] = form['email']
            user['nickname'] = form['nickname']
            g.couch[g.user['id']] = user
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/auth/logout')
def logout():
    """Logout, deletes Session"""
    session.pop('openid', None)
    session.pop('nickname', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())
    

@app.route('/new', methods=['GET', 'POST'])
def new():
    """Creates a new Entry"""
    if g.user is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form['subject']
        text = request.form['edit']
        ttype = request.form['type']
        if not subject:
            flash(u'Error: you have to enter a Subject')
        else:
            flash(u'New Entry successfully created')
	    document = dict(title=subject, type=ttype, content=text, user=g.user['nickname'], date=get_date())
	    g.couch[uuid1().hex] = document	# UUID timebased
	    return redirect(url_for('index'))
    return render_template('new.html')
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Creates a new Entry"""
    if g.user is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form['subject']
        text = request.form['edit']
        ttype = request.form['type']
        if not subject:
            flash(u'Error: you have to enter a Subject')
        else:
            flash(u'New Entry successfully created')
	    document = dict(title=subject, type=ttype, content=text, user=g.user['id'], date=get_date())
	    g.couch[uuid1().hex] = document	# UUID timebased
	    return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/view/web')
def view_web():
    return render_template('web.html')
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        key = request.form.get('search')
    return redirect('/'+ key)

@app.route('/<key>')
def test(key):
    return key
    
if __name__ == '__main__':
  app.run()
