from lib.lilcookies import *
import simplejson as json

COOKIE_SECRET = 'af8559a6788b1ee9fbe34307bc1ac39caf8559a6788b1ee9fbe34307bc1ac39c'

class Session:
    def __init__(self, handler):
        self.cookieutil = LilCookies(handler, COOKIE_SECRET)

    @property
    def data(self):
        try:
            return self._data
        except:
            try:
                self._data = json.loads(self.cookieutil.get_secure_cookie('data'))
            except:
                self._data = {}

            return self._data

    def __getitem__(self, name):
        try:
            return self.data[name]
        except:
            return ''

    def __setitem__(self, name, value):
        self.data[name] = value
        self.cookieutil.set_secure_cookie('data', json.dumps(self.data))

        return value

    def __delitem__(self, name):
        del self.data[name]

        self.cookieutil.set_secure_cookie('data', json.dumps(self.data))
