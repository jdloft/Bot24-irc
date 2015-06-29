# Libraries
import socket

# IRC variables
server = "irc.freenode.net"
channel = "##jdl-testing"
mynick = "Bot24"

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

def parse(s):
    msg = [ # 0 = nick, 1 = user, 2 = host, 3 = target, 4 = message, 5 = privmsg?, 6 = mention?
        s.split( ":" )[ 1 ].split( "!" )[ 0 ], # nick
        s.split( "!" )[ 1 ].split( "@" )[ 0 ], # user
        s.split( " " )[ 0 ].split( "@" )[ 1 ], # host
        s.split( " " )[ 2 ], # target (chan or user)
        ":".join( s.split( ":" )[  2: ] ) # message
    ]
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

# do stuff
print("Connecting socket...")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # start stream
print("Connecting to server...")
ircsock.connect((server, 6667)) # connect to server
print("Authenticating as "+ mynick +"...")
ircsock.send("USER "+ mynick +" "+ mynick +" "+ mynick +" :I annoy people.\n") # user auth
print("Changing nick to "+ mynick +"...")
ircsock.send("NICK "+ mynick +"\n") # nick auth
joinchan(channel) # join channel

while True:
    ircmsg = ircsock.recv(2048) # receive
    ircmsg = ircmsg.strip('\n\r') # clean up

    if ircmsg.find(' PRIVMSG ')!=-1:
        formatmsg = parse(ircmsg)
        print(formatmsg)

    if ircmsg.find("PING :") != -1:
        pong()

    if ircmsg.find(":"+ mynick +": stop") != -1:
        sendmsg(channel, "Stopping...")
        disconnect()
        break
