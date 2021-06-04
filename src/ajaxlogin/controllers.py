# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from hashids import Hashids
from mptools.frameworks.py4web.controller import CORS
from py4web.utils.url_signer import URLSigner
from py4web import action, request, URL

from . import settings
from .tools import IsValidToken

class IdHasher(object):
    """docstring for IdHasher."""

    def __init__(self):
        super(IdHasher, self).__init__()
        self.idhasher = Hashids(salt=settings.DEFAULT_SALT)

    def encode(self, id):
        timestamp = int(datetime.now(timezone.utc).timestamp()*100)
        return self.idhasher.encode(int(id), timestamp)

    def decode(self, hased_id):
        return self.idhasher.decode(hased_id)[0]


def enable(auth, origin='*', token_lifespan=10, use_auth_model=False, test=False):
    """
    """

    idhasher = IdHasher()
    urlsigner = URLSigner(variables_to_sign=['id'], lifespan=token_lifespan)

    # TODO: Support for different method other than PUT

    @action(settings.DEFAULT_NEW_TOKEN_PATH, method=['PUT'])
    @action.uses(CORS(origin=origin), IsValidToken(), urlsigner)
    def newtoken():
        user_id = request.json['user_id']
        return dict(url=URL(settings.DEFAULT_LOGIN_PATH, vars=dict(
            user_id = idhasher.encode(user_id)
        ), signer=urlsigner, scheme='https'))


    @action(settings.DEFAULT_LOGIN_PATH, method=['GET', 'POST'])
    @action.uses(urlsigner.verify(), auth, CORS(origin=origin, session=auth.session))
    def ajaxlogin():

        if auth.user_id is None:

            hased_user_id = request.query.user_id
            user_id = idhasher.decode(hased_user_id)

            if use_auth_model:
                # Login with DB
                user = {}
                user["sso_id"] = "%s:%s" % (origin, user_id)
                user['username'] = user["sso_id"]
                data = auth.get_or_register_user(user)
                auth.store_user_in_session(data['id'])
            else:
                # Login without DB
                auth.store_user_in_session(user_id)

        return dict(
            {'user_id': auth.user_id} if test else {},
            message = 'OK',
        )

    if not test is False:

        @action('testcall', method=['OPTIONS'])
        @action.uses(CORS(origin=origin), auth.session)
        def _():
            return dict()

        @action('testcall', method=['GET', 'POST', 'OPTIONS'])
        @action.uses(auth.session, CORS(origin=origin, session=auth.session), auth.user)
        def _():
            return dict(user_id=auth.user_id)
