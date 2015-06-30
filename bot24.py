# Libraries
import os
import sys
import socket
import sqlite3 as sql
import yaml

# Bot24 stuff:

# main variables
default_channels = ["##jdl-testing", "##jd-jl", "##jdl"]

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
    print("Pong...")
    ircsock.send("PONG :Pong\n")

# send stuff
def sendmsg(target, s):
    ircsock.send("PRIVMSG "+ target +" :"+ s +"\n")

def joinchan(chan):
    print("Joining "+chan)
    ircsock.send("JOIN "+ chan +"\n")

def disconnect():
    print("Disconnecting...")
    ircsock.send("QUIT :Goodbye!\n")
    ircsock.shutdown(1)
    ircsock.close()

# parse PRIVMSGs
def parse(s, msg):
    msg[:] = []
    msg.append(s.split( ":" )[ 1 ].split( "!" )[ 0 ]) # nick
    msg.append(s.split( "!" )[ 1 ].split( "@" )[ 0 ]) # user
    msg.append(s.split( " " )[ 0 ].split( "@" )[ 1 ]) # host
    msg.append(s.split( " " )[ 2 ]) # target (chan or user)
    msg.append(":".join( s.split( ":" )[  2: ] )) # message
    if msg[3][0] == "#":
        msg.append(False)
        if msg[4].find(mynick) != -1:
            msg.append(msg[4].split(mynick+ ": ")[1])
        else:
            msg.append(False)
    else:
        msg.append(True)
        msg.append(msg[4])
    return msg

# DB commands
def getInfo( column, table ):
    dbcur.execute( "SELECT "+ column +" FROM "+ table )
    output = dbcur.fetchall()
    return output

def addInfo( column, table, value ):
    dbcur.execute( "INSERT INTO "+ table +"("+ column +") VALUES ('"+ value +"')")
    if getInfo( column, table ) == value:
        return True
    else:
        return False

# Connect to IRC
print("Connecting socket...")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # start stream
print("Connecting to server...")
ircsock.connect((server, 6667)) # connect to server
print("Authenticating as "+ mynick +"...")
ircsock.send("USER "+ mynick +" "+ mynick +" "+ mynick +" :I annoy people.\n") # user auth
print("Changing nick to "+ mynick +"...")
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

    if ircmsg.find("PING :") != -1:
        pong()

    if ircmsg.find(":"+ mynick +": stop") != -1:
        sendmsg(msg[3], "Stopping...")
        disconnect()
        if db:
            db.close()
        break
