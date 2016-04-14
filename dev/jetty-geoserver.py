#!/usr/bin/env python
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

import glob
import os
import sys

args = [
    '-XX:MaxPermSize=1024m',
    '-Dorg.eclipse.jetty.server.webapp.parentLoaderPriority=true',
    '-DGEOSERVER_DATA_DIR=/vagrant/dev/.geoserver/data',
    '-Duser.home=/vagrant/dev/.geoserver/data/geogig',
    '-jar',
    '/vagrant/dev/.geoserver/jetty-runner-9.3.8.v20160314.jar',
    '--path',
    '/geoserver',
    '/vagrant/dev/.geoserver/geoserver.war'
]
os.execvp('java', args)
