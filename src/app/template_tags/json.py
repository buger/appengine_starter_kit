from google.appengine.ext import webapp
from lib.model_to_json import *
import simplejson as json

register = webapp.template.create_template_register()

@register.filter
def to_json(obj):
    return json.dumps(model_to_json(obj))
