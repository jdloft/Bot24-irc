# Libraries
import socket

# IRC variables
server = "irc.freenode.net"
default_channels = ["##jdl-testing", "##jd-jl", "##jdl"]
mynick = "Bot24"

msg = []
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

# do stuff
print("Connecting socket...")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # start stream
print("Connecting to server...")
ircsock.connect((server, 6667)) # connect to server
print("Authenticating as "+ mynick +"...")
ircsock.send("USER "+ mynick +" "+ mynick +" "+ mynick +" :I annoy people.\n") # user auth
print("Changing nick to "+ mynick +"...")
ircsock.send("NICK "+ mynick +"\n") # nick auth
for chan in default_channels:
    joinchan(chan) # join channels

while True:
    ircmsg = ircsock.recv(2048) # receive
    ircmsg = ircmsg.strip('\n\r') # clean up

    if ircmsg.find(' PRIVMSG ')!=-1:
        parse(ircmsg, msg)
        print(msg)

    if ircmsg.find("PING :") != -1:
        pong()

    if ircmsg.find(":"+ mynick +": stop") != -1:
        sendmsg(msg[3], "Stopping...")
        disconnect()
        break
