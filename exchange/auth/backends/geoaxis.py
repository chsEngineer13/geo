"""
GeoAxis OAuth2 backend:
"""
import ssl

from social.backends.oauth import BaseOAuth2

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
        name = response.get('username') or ''
        fullname, first_name, last_name = self.get_user_names(name)
        return {'username': name,
                'email': response.get('email'),
                'fullname': fullname,
                'firstname': first_name,
                'lastname': last_name}

    def user_data(self, access_token, *args, **kwargs):
        """Grab user profile information from GeoAxis.

        Response:

        {
            "uid": "testuser02",
            "mail": "testuser02@gxis.org",
            "username": "testuser02",
            "DN": "cn=testuser02, OU=People, OU=NGA, OU=DoD, O=U.S. Government, C=US",
            "email": "testuser02@gxis.org",
            "ID": "testuser02",
            "lastname": "testuser02",
            "login": "testuser02",
            "commonname": "testuser02",
            "firstname": "testuser02",
            "personatypecode": "AAA",
            "uri": "\/ms_oauth\/resources\/userprofile\/me\/testuser02"
        }
        
        
        """
        response = self.get_json('https://' + self.HOST + '/ms_oauth/resources/userprofile/me',
                                 params={'access_token': access_token})
        if 'Profile' in response:
            response = {
                'user_id': response['Profile']['CustomerId'],
                'name': response['Profile']['Name'],
                'email': response['Profile']['PrimaryEmail']
            }
        return response
