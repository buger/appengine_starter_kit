import datetime
import time

from google.appengine.ext import db

import simplejson as json

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def model_to_json(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = model_to_json(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    try:
        output['key'] = str(model.key())
    except:
        pass

    return json.loads(json.dumps(output))
