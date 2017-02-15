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

import os

args = [
    '-XX:MaxPermSize=1024m',
    '-Dorg.eclipse.jetty.server.webapp.parentLoaderPriority=true',
    '-DGEOSERVER_DATA_DIR=/tmp/geoserver/data',
    '-Duser.home=/tmp/geoserver/data/geogig',
    '-jar',
    '/tmp/jetty-runner.jar',
    '--path',
    '/geoserver',
    '/tmp/geoserver.war'
]
os.execvp('java', args)
