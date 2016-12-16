# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="geonode-exchange",
    version=__import__('exchange').get_version(),
    author="Boundless Spatial",
    author_email="contact@boundlessgeo.com",
    description="Exchange, a platform for geospatial collaboration",
    long_description=(read('README.rst')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Intended Audience :: System Administrators',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django :: 1.8',
    ],
    license="BSD",
    keywords="exchange geonode django",
    url='https://github.com/boundlessgeo/exchange',
    packages=find_packages('.'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "django-exchange-maploom==1.5.11",
        "geonode==2.5.5",
        "dj-database-url==0.4.1",
        "django-storages==1.1.8",
        "boto==2.38.0",
        "waitress==0.9.0",
        "whitenoise==3.2",
        "django-cors-headers==1.1.0",
        "django-classification-banner==0.1.5",
        "django-solo==1.1.2",
        "django-colorfield==0.1.10",
        "psycopg2==2.6.1",
        "python-ldap==2.4.25",
        "django-auth-ldap==1.2.7",
        "GDAL==2.1.0",
        "supervisor==3.2.3",
        "python-resize-image==1.1.10",
        "django-flat-theme==1.1.3",
        "django-exchange-themes==1.0.3",
        "django-exchange-docs==1.1.2"
    ]
)
