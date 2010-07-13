# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort

from flaskext.couchdb import CouchDBManager
from flaskext.openid import OpenID

app = Flask(__name__)
app.config.update(
    COUCHDB_SERVER = 'http://localhost:5984/',
    COUCHDB_DATABASE = 'brain',
    SECRET_KEY = 'development key',
    DEBUG = True
)

# CouchDB
manager = CouchDBManager()
# ...add document types and view definitions...
manager.setup(app)

# setup flask-openid
oid = OpenID(app)

#----------------------------------------#

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
	g.user = g.couch.get(session['openid'])

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
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
    user = g.couch.get(session['openid'])
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname, nickname=resp.nickname,
                            email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
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
	    document = dict(name=name, email=email, nickname=nickname)
	    g.couch[session['openid']] = document
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        return redirect(url_for('login'))
    form = dict(name=g.user['name'], email=g.user['email'], nickname=g.user['nickname'])
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
            g.user['name'] = form['name']
            g.user['email'] = form['email']
            g.user['nickname'] = form['nickname']
            g.couch[g.user.id] = g.user
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())


if __name__ == '__main__':
  app.run()
