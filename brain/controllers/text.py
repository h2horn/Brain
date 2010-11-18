#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Module, render_template, g, request, flash, url_for, redirect
from uuid import uuid1
from brain.couchviews import *
from brain.helpers import *

text = Module(__name__)

@text.route('/new', methods=['GET', 'POST'])
def new():
    """ Creates a new Text Entry """
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
            document = dict(title=subject, content=text, type=ttype,
                    user=g.user['nickname'], date=get_date())
            g.couch[uuid1().hex] = document # UUID timebased
            return redirect(url_for('index'))
    return render_template('new.html')

@text.route('/upload', methods=['GET', 'POST'])
def upload():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('index.html')

@text.route('/view/web')
def view_web():
    return render_template('web.html')

@text.route('/search')
def search():
    if request.method == 'POST':
        key = request.form.get('search')
    return redirect('/'+key)

@text.route('/')
def index():
    texts = all_text_view()
    for row in texts.rows:
        row['value']['content'] = row['value']['content'][:60]   #TODO
    return render_template('index.html', texts=texts.rows)
