#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flaskext.couchdb import CouchDBManager, ViewDefinition

manager = CouchDBManager() # auto_sync=False

all_users_view = ViewDefinition('users', 'all', '''\
        function (doc) {
            if (doc.type == 'user') {
                emit(doc.openid, null)
            };
        }''')
all_text_view = ViewDefinition('text', 'all', '''\
        function (doc) {
            if (doc.type != 'user') {
                emit(doc.date, {title:doc.title, content: doc.content, user:
                doc.user})
            };
        }''')

manager.add_viewdef((all_users_view, all_text_view))
