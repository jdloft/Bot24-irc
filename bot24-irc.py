# Libraries
import os
import sys
import socket
import sqlite3 as sql
import time
import yaml

msg = []
trusted = False
roles = {}


# Display
def display_clear():
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()


def say(msg, trusted=False, mention=False):
    current_time = time.localtime()
    display_time = time.strftime("%H:%M:%S", current_time)
    #column = "{0:10}{1:10}{2:10}{3:5}{4:20}"
    message = "\033[94m" + display_time + "\033[0m | \033[91m" + msg[3] + "\033[0m | \033[95m" + msg[0]
    if trusted:
        message += "\033[93m*"
    else:
        message += " "

    if mention:
        message += "\033[92m          " + msg[4] + "\033[0m"
    else:
        message += "\033[0m          " + msg[4] + "\033[0m"

    print(message)


def whisper(message, yell=False, component=False):
    current_time = time.localtime()
    display_time = time.strftime("%H:%M:%S", current_time)
    output = "\033[94m" + display_time + "\033[0m | "
    if not component is False:
        output += "\033[92m" + component + ": "
    if yell:
        output += "\033[91m" + message + "\033[0m"
    else:
        output += "\033[90m" + message + "\033[0m"
    print(output)


def respond(message, target):
    current_time = time.localtime()
    display_time = time.strftime("%H:%M:%S", current_time)
    print("\033[94m" + display_time + "\033[0m | " + message + "\033[91m -> " + target + "\033[0m")


# Setup DB
try:
    db = sql.connect('bot24irc.db', isolation_level=None)
    dbcur = db.cursor()
except db.Error, e:
    whisper("Error %s:" % e.args[0], True)
    sys.exit(1)


# Setup config file
with open(os.path.abspath("config.yaml")) as conf:
    config = yaml.load(conf)

mynick = config['credentials']['nick']
password = config['credentials']['password']
server = config['server']


# IRC base actions
# respond to pings
def pong():
    whisper("PONG...")
    ircsock.send("PONG :Pong\n")


# send stuff
def send_msg(target, s, norespond=False):
    if norespond is False:
        respond(s, target)
    ircsock.send("PRIVMSG " + target + " :" + s + "\n")


def join_chan():
    for i in config['channels']:
        whisper("Joining " + i, False, "Channels")
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
                mention = " ".join(msg[4].split(" ")[1:]).lower()  # mention text
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
def get_info(column, table):
    dbcur.execute("SELECT " + column + " FROM " + table)
    output = dbcur.fetchall()
    outputlist = [i for sub in output for i in sub]
    return outputlist


def add_info(table, column, values):
    dbcur.execute("INSERT INTO " + table + "(" + column + ") VALUES ('" + ', '.join(values) + "')")


# Actions
def check_actions(msg):
    # Stop
    if msg[6].startswith("stop"):
        if check_trusted(msg):
            stop()
        else:
            send_msg(msg[3], "Sorry, you can't tell me what to do.")
    # Restart
    elif msg[6].startswith("restart"):
        if check_trusted(msg):
            restart()
        else:
            send_msg(msg[3], "I don't think so.")
    # Role control
    elif msg[6].startswith("role "):
        command = " ".join(msg[6].split(" ")[1:])
        if check_trusted(msg):
            for n in roles:
                if command.startswith(n.lower()):
                    print("Command: <" + command + ">")
                    if command.endswith("start"):
                        send_msg(msg[3], "Starting " + n + "...")
                        roles[n].start()
                        return False
                    elif command.endswith("stop"):
                        send_msg(msg[3], "Stopping " + n + "...")
                        roles[n].stop()
                        return False
                    elif command.endswith("reload"):
                        send_msg(msg[3], "Reloading " + n + "...")
                        roles[n].reload_role()
                        return False
                    else:
                        send_msg(msg[3], "I don't know what you want me to do with this role.")
                        return False
            send_msg(msg[3], "Role not found.")
            return False
        else:
            send_msg(msg[3], "Ha ha ha. Good one.")


def check_trusted(msg):
    trusted_nicks = get_info('Nick', 'TrustedUsers')
    trusted_hosts = get_info('Host', 'TrustedUsers')
    for n in trusted_nicks:
        if msg[0] == n:
            if (msg[2] == trusted_hosts[trusted_nicks.index(n)]):
                return True
            else:
                return False
        else:
            return False


def stop():
    send_msg(msg[3], "Stopping...", True)
    whisper("Stopping...", True)
    time.sleep(2)

    ircsock.send("QUIT :Goodbye!\n")  # seems to not work? Bug #1
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    sys.exit(0)


def restart():
    send_msg(msg[3], "Restarting...", True)
    whisper("Restarting...", True)
    time.sleep(2)

    ircsock.send("QUIT :Restarting\n")
    ircsock.shutdown(1)
    ircsock.close()

    if db:
        db.close()

    executable = sys.executable
    os.execl(executable, executable, * sys.argv)


# Roles
class Role(object):
    run = False
    module_name = ""
    check_func = ""
    args = []

    def init(self):
        if self.module_name:
            try:
                whisper("Importing: " + self.module_name, False, "Roles")
                self.module = __import__(self.module_name)
            except SyntaxError:
                whisper("Syntax error with " + self.module_name + ", skipping...", True, "Roles")
                self.run = False
                return True
            except ImportError:
                whisper("Could not find " + self.module_name + ", skipping...", True, "Roles")
                self.run = False
                return True
            else:
                return False
        else:
            return False

    def start(self):
        self.run = True

    def stop(self):
        self.run = False

    def check(self):
        if self.run:
            if self.module_name:
                return getattr(self.module, self.check_func)(*self.args)
            else:
                return self.check_func(*self.args)
        return ""

    def reload_role(self):
        if self.module:
            try:
                whisper("Reloading " + self.module_name, False, "Roles")
                self.module = reload(self.module)
            except SyntaxError:
                whisper("Syntax error with " + self.module_name + ", skipping...", True, "Roles")
                self.run = False
                return True
            except ImportError:
                whisper("Could not find " + self.module_name + ", skipping...", True, "Roles")
                self.run = False
                return True
            else:
                return False
        return False


def add_role(role_name, run, check_func, args, module):
    roles[role_name] = Role()
    roles[role_name].run = run
    if module:
        roles[role_name].module_name = module
    roles[role_name].check_func = check_func
    roles[role_name].args = args


add_role('phablookup', False, 'lookup', [msg, config['phabricator']['site'], config['phabricator']['apitoken']], 'phablookup')
add_role('keywords', True, 'check', [msg, trusted], 'keywords')

# Do stuff
display_clear()

print("Welcome to Bot24!\n")

whisper("Connecting socket...", False, "Connection")
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start stream

whisper("Connecting to server...", False, "Connection")
ircsock.connect((server, 6667))  # connect to server

whisper("Authenticating as " + mynick + "...", False, "Server")
ircsock.send("USER " + mynick + " " + mynick + " " + mynick + " :In alpha state. Talk to Negative24 with problems.\n")  # user auth

whisper("Setting nick to " + mynick + "...", False, "Server")
ircsock.send("NICK " + mynick + "\n")  # nick auth

whisper("Authenticating with NickServ...", False, "Server")
send_msg('NickServ', "IDENTIFY " + password, True)

join_chan()  # join channels

for n in roles:
    getattr(roles[n], 'init')()  # run init on roles

whisper("Waiting for server...\n", False, "Server")

while True:
    ircmsg = ircsock.recv(4096)  # receive

    for p in ircmsg.splitlines():
        try:
            irccmd = " ".join(p.split(" ")[1:])
        except IndexError:
            irccmd = ""

        if irccmd.startswith("JOIN"):
                whisper("Joined " + irccmd.split(" ")[1], False, "Channels")

    if ircmsg.find(' PRIVMSG ') != -1:
        ircmsg = ircmsg.strip('\n\r')
        parse(ircmsg, msg)

        if check_trusted(msg):
            trusted = True
        else:
            trusted = False

        if (msg[4].find("bot24") != -1) or not (msg[6] is False):
            mention = True
        else:
            mention = False

        say(msg, trusted, mention)

        if not msg[6] is False:
            check_actions(msg)

        # roles
        for n in roles:
            response = getattr(roles[n], 'check')()
            if type(response) is list:
                for response_ln in response:
                    send_msg(msg[3], response_ln)
            else:
                response_lns = response.splitlines()
                for ln in response_lns:
                    if ln == "":
                        ln = " "
                    send_msg(msg[3], ln)

    if ircmsg.find("PING :") != -1:
        pong()
