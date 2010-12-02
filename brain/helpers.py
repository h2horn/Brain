#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import math
from functools import wraps
from flask import g, request, redirect, url_for

def get_date():
    return datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')
#    return datetime.now()

def datetimeformat(value):
    delta = datetime.now() - value
    if delta.days == 0:
        formatting = 'today'
    elif delta.days < 10:
        formatting = '{0} days ago'.format(delta.days)
    elif delta.days < 28:
        formatting = '{0} weeks ago'.format(int(math.ceil(delta.days/7.0)))
    elif value.year == datetime.now().year:
        formatting = 'on %d %b'
    else:
        formatting = 'on %d %b %Y'
    return value.strftime(formatting)

def login_required(f):
    """ Decorator Function redirecting to Login
        if no permission
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
