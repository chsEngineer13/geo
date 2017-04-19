"""
Auth0 OAuth2 backend:
"""
from social_core.backends.oauth import BaseOAuth2

from django.conf import settings


class AuthZeroOAuth2(BaseOAuth2):
    name = 'auth0'
    HOST = getattr(settings, 'SOCIAL_AUTH_AUTH0_HOST', 'auth0.com')
    CLIENT_KEY = getattr(settings, 'SOCIAL_AUTH_AUTH0_KEY', '')
    CLIENT_SECRET = getattr(settings, 'SOCIAL_AUTH_AUTH0_SECRET', '')
    ID_KEY = 'user_id'
    AUTHORIZATION_URL = 'https://{domain}/authorize'.format(domain=HOST)
    ACCESS_TOKEN_URL = 'https://{domain}/oauth/token'.format(domain=HOST)
    USER_INFO_URL = 'https://{domain}/userinfo?access_token={access_token}'
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'

    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('user_id', 'user_id'),
        ('name', 'name'),
        ('email', 'email'),
        ('nickname', 'nickname'),
        ('picture', 'picture'),
        ('groups', 'groups'),
        ('email_verified', 'email_verified'),
    ]

    def get_user_details(self, response):
        """Return user details from Auth0 account"""
        fullname, first_name, last_name = self.get_user_names('',
                                                              response.get('firstname'),
                                                              response.get('lastname'))

        return {'username': response.get('username'),
                'email': response.get('email'),
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}

    def user_data(self, access_token, *args, **kwargs):
        """Grab user profile information from Auth0."""
        response = self.get_json(self.USER_INFO_URL.format(domain=self.HOST, access_token=access_token))
        return response
