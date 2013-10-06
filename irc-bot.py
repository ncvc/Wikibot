#! /usr/bin/env python
#
# Modified from irclib's testbot.py

import irc.bot

from collections import Counter
from time import gmtime

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.counter = Counter()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]

        diff = self.parse_rc(msg)

        if diff == None or diff['title'] == None:
            self.counter[''] += 1
        else:
            self.counter[diff['title']] += 1

        print self.counter.most_common(5)

    def parse_rc(self, msg):
        diff = { 'msg': msg, 'time': gmtime() }

        msg = msg.encode('ascii', 'ignore')

        endTitleIndex = msg.find(']]')
        title = msg[8:endTitleIndex-3]
        diff['title'] = title

        startUrlIndex = msg.find('http://')
        if startUrlIndex == -1:
            return None
        endUrlIndex = msg.find('*', startUrlIndex)
        url = msg[startUrlIndex:endUrlIndex-4]
        diff['url'] = url

        diffType = msg[endTitleIndex+5:startUrlIndex-7]
        diff['type'] = diffType

        endUserIndex = msg.find('*', endUrlIndex+1)
        user = msg[endUrlIndex+6:endUserIndex-4]
        diff['user'] = user

        endBytesIndex = msg.find(')', endUserIndex)
        bytes = msg[endUserIndex+4:endBytesIndex]
        if bytes[0] == '\x02':  # If bold, remove the bold tags
            bytes = bytes[1:-1]
        try:
            diff['bytes'] = int(bytes)
        except ValueError:
            diff['bytes'] = bytes

        comments = msg[endBytesIndex+5:-1]
        diff['comments'] = comments

        return diff

    def do_command(self, e, cmd):
        return
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.notice(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        else:
            c.notice(nick, "Not understood: " + cmd)


def startBot(server, nickname, channel, port=6667):
    bot = TestBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    startBot('irc.wikimedia.org', 'wikibot', '#en.wikipedia')
