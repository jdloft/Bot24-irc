# Libraries
import os
import sys
import socket
import sqlite3 as sql
import yaml

import keywords

msg = []
roles = []

# Setup DB
try:
    db = sql.connect('bot24irc.db', isolation_level=None)
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
    print("PONG...")
    ircsock.send("PONG :Pong\n")


# send stuff
def sendmsg(target, s):
    ircsock.send("PRIVMSG " + target + " :" + s + "\n")


def joinchan():
    for i in config['channels']:
        print("Joining " + i)
        ircsock.send("JOIN " + i + "\n")


# parse PRIVMSGs
def parse(s, msg):
    msg[:] = []   # 0 = nick, 1 = user, 2 = host, 3 = target, 4 = message, 5 = privmsg?, 6 = mention
    msg.append(s.split(":")[1].split("!")[0])  # nick
    msg.append(s.split("!")[1].split("@")[0])  # user
    msg.append(s.split(" ")[0].split("@")[1])  # host
    msg.append(s.split(" ")[2])  # target (chan or user)
    msg.append(":".join(s.split(":")[2:]))  # message
    if msg[3][0] == "#":
        msg.append(False)  # privmsg?
        if(msg[4][:len(mynick)] == mynick):
            try:
                mention = msg[4].split(" ")[1]  # mention text
            except IndexError:
                mention = " "
            msg.append(mention)
        else:
            msg.append(False)
    else:
        msg.append(True)
        msg.append(msg[4].split(" ")[1])
    return msg


# DB commands
def getInfo(column, table):
    dbcur.execute("SELECT " + column + " FROM " + table)
    output = dbcur.fetchall()
    outputlist = [i for sub in output for i in sub]
    return outputlist


def addInfo(table, column, values):
    dbcur.execute("INSERT INTO " + table + "(" + column + ") VALUES ('" + ', '.join(values) + "')")


# Actions
def checkActions(msg):
    if msg[6] == "stop":
        if checkTrusted(msg):
            stop()
        else:
            sendmsg(msg[3], "Sorry, you can't tell me what to do.")
    elif msg[6] == "restart":
        if checkTrusted(msg):
            restart()
        else:
            sendmsg(msg[3], "No. I just haven't met you yet.")


def checkTrusted(msg):
    trustedNicks = getInfo('Nick', 'TrustedUsers')
    trustedHosts = getInfo('Host', 'TrustedUsers')
    for n in trustedNicks:
        if msg[0] == n:
            if (msg[2] == trustedHosts[trustedNicks.index(n)]):
                return True
            else:
                return False
        else:
            return False


def stop():
    sendmsg(msg[3], "Stopping...")
    print("Stopping...")

    ircsock.send("QUIT :Goodbye!\n")  # seems to not work? Bug #1
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    sys.exit(0)


def restart():
    sendmsg(msg[3], "Restarting...")
    print("Restarting...")

    ircsock.send("QUIT :Restarting\n")
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    executable = sys.executable
    os.execl(executable, executable, * sys.argv)


class colors:
    header = '\033[1m'
    ok = '\033[92m'
    info = '\033[94m'
    warning = '\033[1m\033[93m'
    fail = '\033[1m\033[91m'
    reset = '\033[0m'


class role:
    run = False
    moduleName = ""
    checkFunc = ""
    args = []

    def init(self):
        if self.moduleName:
            try:
                print("Importing: " + self.moduleName)
                self.module = __import__(self.moduleName)
            except SyntaxError:
                print("Syntax error with " + self.moduleName + ", skipping...")
                self.run = False
                return 1
            except ImportError:
                print("Could not find " + self.moduleName + ", skipping...")
                self.run = False
                return 1
            else:
                self.funcToCall = getattr(self.module, self.checkFunc)
                return 0
        else:
            return 0

    def stop(self):
        self.run = False

    def start(self):
        self.run = True

    def check(self):
        if self.run:
            if self.moduleName:
                results = self.funcToCall(*self.args)
            else:
                results = self.checkFunc(*self.args)
            return results
        else:
            return ""

    def reload(self):
        if self.module:
            try:
                reload(self.module)
            except SyntaxError:
                print("Syntax error with " + self.module + ", skipping...")
                self.run = False
                return 1
            except ImportError:
                print("Could not find " + self.module + ", skipping...")
                self.run = False
                return 1
            else:
                return 0
        else:
            return 0

phabLookup = role()
roles.append(phabLookup)
phabLookup.run = True
phabLookup.moduleName = 'phablookup'
phabLookup.checkFunc = 'lookup'
phabLookup.args = [msg, config['phabricator']['site'], config['phabricator']['apitoken']]

# Do stuff
print("Connecting socket...")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start stream
print("Connecting to server...")
ircsock.connect((server, 6667))  # connect to server
print("Authenticating as " + mynick + "...")
ircsock.send("USER " + mynick + " " + mynick + " " + mynick + " :In alpha state. Talk to Negative24 with problems.\n")  # user auth
print("Setting nick to " + mynick + "...")
ircsock.send("NICK " + mynick + "\n")  # nick auth
print("Authenticating with NickServ...")
sendmsg('NickServ', "IDENTIFY " + password)
joinchan()  # join channels

phabLookup.init()

while True:
    ircmsg = ircsock.recv(2048)  # receive
    ircmsg = ircmsg.strip('\n\r')  # clean up

    #print(ircmsg)

    if ircmsg.find(' PRIVMSG ') != -1:
        parse(ircmsg, msg)
        print(msg)

        if not msg[6] is False:
            checkActions(msg)

        # roles
        for role in roles:
            for response in getattr(role, 'check')():
                sendmsg(msg[3], response)

        # keywords lookup
        if checkTrusted(msg):
            response = keywords.check(msg, True)
        else:
            response = keywords.check(msg, False)
        responselns = response.splitlines()
        for ln in responselns:
            if ln == '':
                ln = " "
            sendmsg(msg[3], ln)

    if ircmsg.find("PING :") != -1:
        pong()
