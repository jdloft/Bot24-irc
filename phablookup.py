
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

import json
import subprocess
import re
import os


def lookup(msg, site, apitoken):
    matches = []
    text = []
    if (msg[0] == "wikibugs" or msg[0] == "grrrit-wm"):
        return ""
    matches = re.findall(r"https?://phabricator.wikimedia.org/[T][1-9][0-9]{0,6}(?=\W|\Z)", msg[4])
    if matches:
        showurl = False
        for s, value in enumerate(matches):
            matches[s] = matches[s].rsplit("/", 1)[-1]
    else:
        showurl = True
        matches = re.findall(r"[T][1-9][0-9]{0,6}(?=\W|\Z)", msg[4])
    for n in matches:
        print("Looking up " + n)
        if n.startswith("T"):
            print("Maniphest task")
            request = """{
                          "task_id": """ + n[1:] + """
                      }"""
            method = "maniphest.info"
            title = get_title(request, method, n[1:], 'title', site, apitoken)
            if (title == "Doesn't exist" or title == "Error with lookup"):
                showurl = False
            if showurl:
                text.append(n + ": " + title + " - " + site + "/" + n)
            else:
                text.append(n + ": " + title)
        #  elif matches[n][:1] == "D": # Differential support
    return text


def get_title(request, method, refnum, refprop, site, token):
    arc = os.path.abspath("arcanist/bin/arc")
    arc_cmd = [arc, "call-conduit", "--conduit-uri=" + site, "--conduit-token=" + token, method]
    phabreq = subprocess.Popen(arc_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        phabjson = json.loads(phabreq.communicate(request)[0])
    except ValueError:
        return ""
    else:
        if not phabjson['error'] is None:
            if phabjson['error'] == "ERR_BAD_TASK":
                response = "Doesn't exist"
            else:
                response = "Error with lookup"
        else:
            response = phabjson['response'][refprop]
        return response
