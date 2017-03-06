"""
GeoAxis OAuth2 backend:
"""
import ssl

from social_core.backends.oauth import BaseOAuth2

from django.conf import settings


class GeoAxisOAuth2(BaseOAuth2):
    name = 'geoaxis'
    HOST = getattr(settings, 'SOCIAL_AUTH_GEOAXIS_HOST', 'localhost')
    ID_KEY = 'user_id'
    AUTHORIZATION_URL = 'https://' + HOST + '/ms_oauth/oauth2/endpoints/oauthservice/authorize'
    ACCESS_TOKEN_URL = 'https://' + HOST + '/ms_oauth/oauth2/endpoints/oauthservice/tokens'
    DEFAULT_SCOPE = ['UserProfile']
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    SSL_PROTOCOL = ssl.PROTOCOL_TLSv1
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('user_id', 'user_id'),
        ('postal_code', 'postal_code')
    ]

    def get_user_details(self, response):
        """Return user details from GeoAxis account"""
        fullname, first_name, last_name = self.get_user_names('',
                                                              response.get('firstname'),
                                                              response.get('lastname'))
        return {'username': response.get('username'),
                'email': response.get('email'),
                'fullname': fullname,
                'firstname': first_name,
                'lastname': last_name}

    def user_data(self, access_token, *args, **kwargs):
        """Grab user profile information from GeoAxis.

        Response:

        {
            "uid": "testuser",
            "mail": "testuser@gxis.org",
            "username": "testuser",
            "DN": "cn=testuser, OU=People, OU=Unit, OU=DD, O=Example, C=US",
            "email": "testuser@gxis.org",
            "ID": "testuser",
            "lastname": "testuser",
            "login": "testuser",
            "commonname": "testuser",
            "firstname": "testuser",
            "personatypecode": "AAA",
            "uri": "\/ms_oauth\/resources\/userprofile\/me\/testuser"
        }
        
        
        """
        response = self.get_json('https://' + self.HOST + '/ms_oauth/resources/userprofile/me',
                                 params={'access_token': access_token})
        return response
