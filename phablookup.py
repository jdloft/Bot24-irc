import json
import subprocess
import re

def lookup( msg, site, apitoken ):
    wordlist = msg[4].split(" ")
    matches = []
    text = []
    regex = re.compile( r"[T][1-9][0-9]{0,6}(?=\W|\Z)" ) # matching standalone T# to T#####
    regex2 = re.compile( r"https?://phabricator.wikimedia.org/[T][1-9][0-9]{0,6}(?=\W|\Z)" )
    for w in wordlist:
        if regex2.match( w ):
            print("Matched regex2")
            showurl = False
            w = w.rsplit( "/", 1 )[1]
            w = re.sub( r'(?![T][1-9][0-9]{0,6})\W+', '', w )
            matches.append( w )
        else:
            print("Regex1 check...")
            showurl = True
            w = re.sub( r'\W+', '', w ) # strip out non-alphanumeric chars (punctuation and such)
            if regex.match( w ):
                print("Matched regex1")
                matches.append( w )
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
                text.append( n +": "+ title +" - "+ site +"/"+ n[1:] )
            else:
                text.append( n +": "+ title )
        #elif matches[n][:1] == "D": # Differential support
    return text

def getTitle( request, method, refnum, refprop, site, token ):
    arc_cmd = [ "arc", "call-conduit", "--conduit-uri="+ site, "--conduit-token="+ token, method ]
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
