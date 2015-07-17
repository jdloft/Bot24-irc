#!/usr/bin/python

# Bot24-irc - An IRC bot with misc tools for Wikimedia channels
# Copyright (C) 2015 Jamison Lofthouse
#
# This file is part of Bot24-irc.
#
# Bot24-irc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bot24-irc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bot24-irc.  If not, see <http://www.gnu.org/licenses/>.


import sqlite3 as lite
import sys

con = lite.connect('bot24irc.db')

with con:
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE TrustedUsers(Nick TEXT, User TEXT, Host TEXT);
        CREATE TABLE Channels(Channel TEXT, Password TEXT);
        """)