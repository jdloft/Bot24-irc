#!/usr/bin/python

import sqlite3 as lite
import sys

con = lite.connect('bot24irc.db')

with con:
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE TrustedUsers(Nick TEXT, User TEXT, Host TEXT);
        CREATE TABLE Channels(Channel TEXT, Password TEXT);
        """)
