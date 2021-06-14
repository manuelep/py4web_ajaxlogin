# -*- coding: utf-8 -*-

from mptools.frameworks.py4web.controller import CORS
from py4web.utils.url_signer import URLSigner
from py4web import action, request, URL, redirect
from py4web.utils.factories import ActionFactory

from . import settings
from .tools import IsValidToken

from .common import LoginChecker

class FixtureChain(object):
    """docstring for FixtureChain."""

    def __init__(self, *fixtures):
        super(FixtureChain, self).__init__()
        self.fixtures = fixtures

    def __call__(self, *fixtures):
        return self.fixtures+fixtures

    def push(self, *fixtures):
        self.fixtures = fixtures+self.fixtures


def enable(auth, origin='*', token_lifespan=10, use_auth_model=False, test=False):
    """ """

    loginchecker = LoginChecker(auth, origin=origin, use_auth_model=use_auth_model)
    urlsigner = URLSigner(variables_to_sign=['id'], lifespan=token_lifespan)

    # TODO: Support for different method other than PUT

    @action(settings.DEFAULT_NEW_TOKEN_PATH, method=['PUT'])
    @action.uses(CORS(origin=origin), IsValidToken(), urlsigner)
    def intercom():
        user_id = request.json['user_id']
        dest = request.json.get('dest', settings.DEFAULT_LOGIN_PATH)
        return dict(url=URL(dest, vars=dict(
            hashed_user_id = loginchecker.encode(user_id)
        ), signer=urlsigner, scheme='https'))

    @action(settings.DEFAULT_LOGIN_PATH, method=['GET', 'POST'])
    @action.uses(urlsigner.verify(), loginchecker, CORS(origin=origin, session=auth.session))
    def ajaxlogin():
        return dict(
            {'user_id': auth.user_id} if test else {},
            message = 'OK' if auth.user_id else 'ANONYMOUS',
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

    return ActionFactory(loginchecker, urlsigner, CORS(origin=origin, session=auth.session))
