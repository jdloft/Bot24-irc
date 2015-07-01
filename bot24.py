# Libraries
import os
import sys
import socket
import sqlite3 as sql
import yaml

# main variables
default_channels = ["##bot24", "##jd-jl", "##jdl"]

msg = []

# Setup DB
try:
    db = sql.connect( 'bot24irc.db', isolation_level=None )
    dbcur = db.cursor()
except db.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)

# Setup config file
with open(os.path.abspath("config.yaml")) as conf:
    config = yaml.load(conf)

mynick = config['credentials']['nick']
password = config['credentials']['password']
server = config['server']

# IRC actions
# respond to pings
def pong():
    print( "Pong..." )
    ircsock.send( "PONG :Pong\n" )

# send stuff
def sendmsg( target, s ):
    ircsock.send( "PRIVMSG "+ target +" :"+ s +"\n" )

def joinchan( chan ):
    print( "Joining "+ chan )
    ircsock.send( "JOIN "+ chan +"\n" )

# parse PRIVMSGs
def parse(s, msg):
    msg[:] = [] # 0 = nick, 1 = user, 2 = host, 3 = target, 4 = message, 5 = privmsg?, 6 = mention
    msg.append(s.split( ":" )[ 1 ].split( "!" )[ 0 ]) # nick
    msg.append(s.split( "!" )[ 1 ].split( "@" )[ 0 ]) # user
    msg.append(s.split( " " )[ 0 ].split( "@" )[ 1 ]) # host
    msg.append(s.split( " " )[ 2 ]) # target (chan or user)
    msg.append(":".join( s.split( ":" )[  2: ] )) # message
    if msg[3][0] == "#":
        msg.append(False) # privmsg?
        if( msg[4][:len( mynick )] == mynick ):
            msg.append( msg[4].split(" ")[1] ) # mention text
        else:
            msg.append( False )
    else:
        msg.append( True )
        msg.append( msg[4].split(" ")[1] )
    return msg

# DB commands
def getInfo( column, table ):
    dbcur.execute( "SELECT "+ column +" FROM "+ table )
    output = dbcur.fetchall()
    outputlist = [i for sub in output for i in sub]
    return outputlist

def addInfo( table, values ):
    dbcur.execute( "INSERT INTO "+ table +"("+ column +") VALUES ('"+ ', '.join(values) +"')")

# Actions
def checkActions( msg ):
    if msg[6] == "stop":
        if checkTrusted( msg ):
            stop()
    elif msg[6] == "restart":
        if checkTrusted( msg ):
            restart()

def checkTrusted( msg ):
    trustedNicks=getInfo( 'Nick', 'TrustedUsers')
    trustedHosts=getInfo( 'Host', 'TrustedUsers')
    for n in trustedNicks:
        if msg[0] == n:
            if ( msg[2] == trustedHosts[ trustedNicks.index(n) ]  ):
                return True
            else:
                sendmsg( msg[3], "You are not a trusted user. Sorry." )
                return False
        else:
            sendmsg( msg[3], "You are not a trusted user. Sorry." )
            return False

def stop():
    sendmsg( msg[3], "Stopping..." )
    print("Stopping...")

    ircsock.send("QUIT :Goodbye!\n") # seems to not work? Bug #1
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    sys.exit(0)

def restart():
    sendmsg( msg[3], "Restarting..." )
    print( "Restarting..." )

    ircsock.send("QUIT :Restarting\n")
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    executable = sys.executable
    os.execl( executable, executable, * sys.argv)

# Connect to IRC
print("Connecting socket...")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # start stream
print("Connecting to server...")
ircsock.connect((server, 6667)) # connect to server
print("Authenticating as "+ mynick +"...")
ircsock.send("USER "+ mynick +" "+ mynick +" "+ mynick +" :I annoy people.\n") # user auth
print("Setting nick to "+ mynick +"...")
ircsock.send("NICK "+ mynick +"\n") # nick auth
print("Authenticating with NickServ...")
sendmsg('NickServ', "IDENTIFY "+ password)
for chan in default_channels:
    joinchan(chan) # join channels

while True:
    ircmsg = ircsock.recv(2048) # receive
    ircmsg = ircmsg.strip('\n\r') # clean up

    print( ircmsg )

    if ircmsg.find(' PRIVMSG ')!=-1:
        parse(ircmsg, msg)
        print(msg)

        if not msg[6] == False:
            checkActions( msg )

    if ircmsg.find("PING :") != -1:
        pong()
