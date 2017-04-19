#
# Setup a parent class for Exchange tests
#  that handles commmon operations.
#

import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

import os.path

TESTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')


class ExchangeTest(TestCase):

    def setUp(self):
        django.setup()

    def get_file_path(self, filename):
        global TESTDIR
        return os.path.join(TESTDIR, filename)

    def login(self):
        User = get_user_model()

        self.client = Client()
        admin_users = User.objects.filter(
            is_superuser=True
        )
        if admin_users.count() > 0:
            self.admin_user = admin_users[0]
        else:
            self.admin_user = User.objects.create_superuser(
                username='admin',
                email=''
            )
        self.admin_user.set_password('admin')
        self.admin_user.save()
        logged_in = self.client.login(
            username='admin',
            password='admin'
        )
        self.assertTrue(logged_in)

        self.expected_status = 200

        return True
