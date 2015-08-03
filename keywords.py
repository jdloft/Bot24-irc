
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


def check(msg, trusted):
    response = ""
    if not msg[6] is False:
        if msg[6] == "help":
            if trusted:
                response = """Bot24 - Help
Commands:
help - this help text

Trusted user commands:
stop - shutdown bot
restart - restart bot"""
            else:
                response = """Bot24 - Help
Commands:
help - this help text"""
        elif (msg[6] == "hi" or msg[6] == "hello"):
            response = "hello!"
    else:
        if msg[4].find("bot24") != -1:
            response = "o/"
    return response
