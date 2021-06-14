# -*- coding: utf-8 -*-

from . import settings
from hashids import Hashids
from datetime import datetime, timezone
import calendar, time
from py4web.core import Fixture
from mptools.frameworks.py4web.controller import web_call
from py4web import request, abort, HTTP
from urllib.parse import urlparse

class IdHasher(object):
    """docstring for IdHasher."""

    def __init__(self):
        super(IdHasher, self).__init__()
        self.idhasher = Hashids(salt=settings.DEFAULT_SALT)

    def encode(self, id):
        timestamp = int(datetime.now(timezone.utc).timestamp()*100)
        return self.idhasher.encode(int(id), timestamp)

    def decode(self, hased_id):
        decoded = self.idhasher.decode(hased_id)
        if decoded:
            return decoded[0]
        else:
            abort(401, "Wrong code")

idhasher = IdHasher()

class LoginChecker(Fixture):
    """docstring for LoginChecker."""

    def __init__(self, auth, origin, use_auth_model=False):
        super(LoginChecker, self).__init__()
        self.auth = auth
        self.use_auth_model = use_auth_model
        self.origin = origin

    encode = lambda self, id: idhasher.encode(id)
    decode = lambda self, hashed_id: idhasher.decode(hashed_id)

    def __auth_login(self, user_id, email):
        if self.use_auth_model:
            # Login with DB
            user = {}
            origin = urlparse(request.headers.environ.get("HTTP_ORIGIN", self.origin)).hostname
            user["sso_id"] = f"{origin}:{user_id}"
            user['username'] = user["sso_id"]
            user['email'] = f"user_{user_id}@{origin}"
            data = self.auth.get_or_register_user(user)
            assert data
            self.auth.store_user_in_session(data['id'])
        else:
            # Login without DB
            self.auth.store_user_in_session(user_id)
        assert self.auth.user_id

    def __call__(self, hashed_user_id, email=None, **__):
        """ Decode the remote user_id and use it for login """

        # The user could be logged in but the session could be expired
        # Courtesy of: https://github.com/web2py/py4web/blob/master/py4web/utils/auth.py#L95
        if not self.auth.user_id is None:
            activity = self.auth.session.get("recent_activity")
            time_now = calendar.timegm(time.gmtime())
            if self.auth.param.login_expiration_time and activity:
                if time_now - activity > self.auth.param.login_expiration_time:
                    self.auth.session.clear()

        if self.auth.user_id is None:
            user_id = self.decode(hashed_user_id)
            self.__auth_login(user_id, email=email)

    def on_request(self):
        web_call(self)
