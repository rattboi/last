# last replacement for #music

from twisted.internet import ssl, reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.words.protocols import irc
from commands import Commands
from db import Contacts
import pylast
import secrets


class Contact(object):

    def __init__(self, user, channel):
        self.user = user
        self.channel = channel
        self.nick = self._nick(user)
        self.last = None
        self.private = False

    def __repr__(self):
        return ("IRC Contact for %s: channel=%s, nick=%s, last=%r, private=%s"
                % (self.user, self.channel, self.nick, self.last, self.private))

    def _nick(self, user):
        return user.split('!', 1)[0]

    def setLastUser(self, last):
        self.last = last


class Bot(irc.IRCClient):

    def __init__(self, nickname, chans, fact):
        self.nickname = nickname
        self.chans = chans
        self.factory = fact
        self.db = Contacts()
        self.commands = Commands(self)
        self.last = pylast.LastFMNetwork(api_key=secrets.API_KEY,
                                         api_secret=secrets.API_SECRET,
                                         username=secrets.username,
                                         password_hash=secrets.password_hash)

    def _isPrivate(self, nick, channel):
        return (channel == self.nickname and nick != self.nickname)

    def signedOn(self):
        for chan in self.chans:
            self.join(chan)

    def msg(self, contact, message):
        channel = contact.nick if contact.private else contact.channel
        irc.IRCClient.msg(self, channel, message)

    def privmsg(self, user, channel, message):
        contact = self.db.get(user)

        # update private context for replies to existing contact
        if contact:
            private = self._isPrivate(contact.nick, channel)
            contact.channel = channel
            contact.private = private
        # if new contact, create and set private context
        else:
            contact = Contact(user, channel)
            contact.private = self._isPrivate(contact.nick, channel)
            self.db.set(contact.user, contact)

        if contact.private or message.startswith("#"):
            self.commands.parse(contact, message)


class BotFactory(ReconnectingClientFactory):

    protocol = Bot

    def __init__(self, nick, chans):
        self.nick = nick
        self.chans = chans

    def buildProtocol(self, addr):
        return self.protocol(self.nick, self.chans, self)

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

if __name__ == "__main__":
    from subprocess import call
    call(["redis-server", "redis.conf"])

    server = "irc.cat.pdx.edu"
    port = 6697
    nickname = "last_"
    channels = ["#botgrounds"]
    factory = BotFactory(nickname, channels)

    reactor.connectSSL(server, port, factory, ssl.ClientContextFactory())
    reactor.run()
