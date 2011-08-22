from google.appengine.ext import webapp
from google.appengine.ext import db

from time import time
import os

register = webapp.template.create_template_register()

@register.filter
def stylesheet(name, rel = None):
    if rel is None:
        rel = "stylesheet"
    else:
        rel = "stylesheet/%s" % rel

    return "<link rel='%s' type='text/css' href='/css/%s.css?%d'>" % (rel, name, time())

@register.filter
def javascript(name):
    return "<script src='/js/%s.js?%d'></script>" % (name, time())
