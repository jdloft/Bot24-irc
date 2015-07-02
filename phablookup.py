import json
import subprocess
import re
import os

def lookup( msg, site, apitoken ):
    wordlist = msg[4].split(" ")
    matches = []
    text = []
    if ( msg[0] == "wikibugs" or msg[0] == "grrrit-wm" ):
        return ""
    matches = re.findall( r"https?://phabricator.wikimedia.org/[T][1-9][0-9]{0,6}(?=\W|\Z)", msg[4] )
    if matches:
        showurl = False
    else:
        showurl = True
        matches = re.findall( r"[T][1-9][0-9]{0,6}(?=\W|\Z)", msg[4] )
    for n in matches:
        if n[:1] == "T":
            request = """{
                          "task_id": """+ n[1:] +"""
                      }"""
            method = "maniphest.info"
            print("Looking up "+ n)
            title = getTitle( request, method, n[1:], 'title', site, apitoken )
            if ( title == "Doesn't exist" or title == "Error with lookup" ): showurl = False
            if showurl:
                text.append( n +": "+ title +" - "+ site +"/"+ n )
            else:
                text.append( n +": "+ title )
        #elif matches[n][:1] == "D": # Differential support
    return text

def getTitle( request, method, refnum, refprop, site, token ):
    arc = os.path.abspath( "arcanist/bin/arc" )
    arc_cmd = [ arc, "call-conduit", "--conduit-uri="+ site, "--conduit-token="+ token, method ]
    print( "Looking up "+ refnum )
    phabreq = subprocess.Popen( arc_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    phabjson = json.loads( phabreq.communicate( request )[0] )
    if not phabjson['error'] == None:
        if phabjson['error'] == "ERR_BAD_TASK":
            response = "Doesn't exist"
        else:
            response = "Error with lookup"
    else:
        response = phabjson['response'][refprop]
    return response
