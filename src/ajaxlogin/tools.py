# -*- coding: utf-8 -*-

from py4web import request, abort
from py4web.core import Fixture
from base64 import b64decode

from . import settings

class IsValidToken(Fixture):
    """docstring for IsValidToken."""

    def __init__(self, token=settings.DEFAULT_TOKEN):
        super(IsValidToken, self).__init__()
        self.TOKEN = token

    @staticmethod
    def __get_token():
        encoded = request.headers['Authorization'].replace('Bearer ', '')
        return b64decode(encoded)

    def on_request(self):

        token = self.__get_token()
        if token!=self.TOKEN:
            abort(401, 'Unrecognized token')
        # elif self.TOKEN==settings.DEFAULT_TOKEN and not request.urlparts.netloc.startswith('localhost'):
        #     abort(403)
            # raise HTTP(403)
