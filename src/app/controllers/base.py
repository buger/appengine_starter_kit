import re
import os
import random
import md5
import urllib
import logging

import simplejson as json

from app.models import *

from lib.counter import *
from lib.secure_cookie_session import CookieSession
from lib.model_to_json import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import users

template.register_template_library('app.template_tags.media_tag')
template.register_template_library('app.template_tags.with_tag')
template.register_template_library('app.template_tags.json')

def is_production_mode():
    return os.environ['SERVER_NAME'] != 'localhost'


class AppHandler(webapp.RequestHandler):
    def guess_lang(self):
        lang = self.request.get('lang')

        if lang:
            if lang != 'en' and lang != 'ru':
                lang = 'en'

            os.environ['i18n_lang'] = lang
        else:
            os.environ['i18n_lang'] = 'en'

        return os.environ['i18n_lang']

    @property
    def login_url(self):
        return users.create_login_url(self.request.uri)
    
    @property
    def logout_url(self):
        return users.create_logout_url(self.request.uri)

    def render_template(self, name, data = None):
        self.guess_lang()

        path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)),'views', name))

        if data is None:
            data = {}

        if not data.has_key('admin'):
            data['admin'] = users.is_current_user_admin()

        data.update({
            'user': users.get_current_user(),
            'lang': os.environ['i18n_lang'],
            'session': self.session,            
            'production': is_production_mode(),

            'login_url': self.login_url,
            'logout_url': self.logout_url
        })
       
        html = template.render(path, data)

        if not data.has_key('dont_render'):
            self.response.out.write(html)

        try:
            del self.session['flash']
        except:
            pass

        return html

    
    def render_json(self, data, status = None):
        if status:
            self.response.set_status(status)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(data))        

    def render_text(self, string):
        self.response.headers['Content-Type'] = 'text'
        self.response.out.write(string)

    # Example:
    #   self.session['data']
    #   self.session['data'] = 'adasdasd'
    #   del self.session['data']
    #
    # Using Flash:
    #   self.session['flash'] = 'asdasd']
    #   self.session['flash'] <- After getting it deletes 'flash' key
    @property
    def session(self):
        try:
            return self._session
        except AttributeError:
            self._session = CookieSession(self)
            return self._session    




routes = {}

# route('/', StaticPage)
# route('/:template', StaticPage)
# route('/', DomainStaticPage, 'my')
def route(string, handler, subdomain = 'www'):
    if subdomain not in routes:
        routes[subdomain] = []

    # convert /edit/:user_id to /edit/([^/]+)?
    string = re.sub("\:([^/]+)?", '([^/]+)?', string)
    routes[subdomain].append([string, handler])

def start():
    if 'HTTP_HOST' in os.environ:
        http_full_host = os.environ['HTTP_HOST']
    else:
        http_full_host = 'localhost'

    subdomain = re.match("(\w+)\.", http_full_host)

    app_routes = []

    if subdomain is None:
        for k,v in routes.items():
            for r in v:
                app_routes.append(r)
    else:
        subdomain = subdomain.group(1)

        if subdomain in routes:
            for r in routes[subdomain]:
                app_routes.append(r)

    application = webapp.WSGIApplication(app_routes, debug=True)
    run_wsgi_app(application)

class RoutesViewer(AppHandler):
    def get(self):
        text = []

        for subdomain in routes:
            text.append(subdomain)

            sorted_routes = sorted(routes[subdomain])

            for route in sorted_routes:
                text.append("\n\t%s %s" % (route[0].ljust(40), str(route[1])))

        self.render_text("".join(text))

route('/admin/routes', RoutesViewer)             


class Devnull(AppHandler):
    def get(self):
        self.error(200)

    def post(self):
        self.get()

route('/devnull', Devnull)
