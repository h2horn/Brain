# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, session

from brain.controllers.auth import auth, oid
from brain.controllers.text import text

app = Flask(__name__)

#Config
app.config.from_pyfile('../config')

#Module
app.register_module(auth)   # url_prefix='/auth'
app.register_module(text)
oid.init_app(app)
from brain.couchviews import manager
manager.setup(app)
#manager.sync(app)

@app.before_request
def before_request():
    g.user = None
    if 'nickname' in session:
        g.user = session
