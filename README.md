# bot24-irc
[![Travis](https://img.shields.io/travis/jdloft/bot24-irc.svg)](https://travis-ci.org/jdloft/bot24-irc)
[![Code Climate](https://img.shields.io/codeclimate/github/jdloft/bot24-irc.svg)](https://codeclimate.com/github/jdloft/bot24-irc)
[![GitHub release](https://img.shields.io/github/release/jdloft/bot24-irc.svg)](https://github.com/jdloft/bot24-irc/releases)

Bot24-irc is the IRC component of the Bot24 framework.
At the moment it doesn't do much at the moment. It relies
on roles, just pieces of functionality built into modules
and then translated through a class or just built into the
class itself.


## Installation
1. Run `sqlinit.py` to generate the database file
2. Duplicate sample-config.yaml and fill in with your details

## IRC commands

### Mentioning for commands
The bot can be controlled by mentioning it at the beginning
of the message with or without a colon. For example, a
bot with the nick `bot24` (I'm creative) can be mentioned
with `bot24: command` and `bot24 command`.

### Main bot control
* `stop` disconnects from server, cleans up, and exits
* `restart` stops and then restarts the script

### Role control
* `role` precedes all role control commmands
  * `role ROLE status` checkes the state of `ROLE`
  * `role ROLE start` starts `ROLE`
  * `role ROLE stop` stops `ROLE`
  * `role ROLE reload` reloads `ROLE` if it is a module

## Flags
* `--debug` outputs all raw IRC messages
* `--plain` doesn't output any ANSI control characters
(color and screen clearing)

## Roles
The roles `phablookup` and `keywords` come installed (but
`phablookup` disabled). `phablookup` lookes up any
Phabricator Maniphest Task number such as T##### or
http://url.something.com/T####. `keywords` lookes up keywords
that are defined in its module.
