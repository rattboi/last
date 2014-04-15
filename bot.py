# last replacement for #music

from twisted.internet import ssl, reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.words.protocols import irc
from commands import Commands
from youtube import Youtube
from db import Contacts
import pylast
import secrets


class Contact(object):
    """One user's identity to the Bot

    This keeps track of a user's current info for the Bot, including last.fm
    account info and current channel for messaging.
    """

    def __init__(self, user, channel):
        """set initial context of user"""
        self.user = user
        self.channel = channel
        self.nick = self._nick(user)
        self.last = None
        self.private = False

    def __repr__(self):
        return ("IRC Contact for %s: channel=%s, nick=%s, last=%r, private=%s"
                % (self.user, self.channel, self.nick, self.last, self.private))

    def _nick(self, user):
        """trim hostmask"""
        return user.split('!', 1)[0]

    def setLastUser(self, last):
        """set last.fm info"""
        self.last = last


class Bot(irc.IRCClient):
    """Core Bot events, subclassed from Twisted's IRCClient

    Respond to privmsgs in channels and wrap self.msg to delegate replies
    based on the context (query versus public channel). This also maintains
    the Redis and last.fm connections while creating contacts as users talk.
    """

    def __init__(self, nickname, chans, fact):
        """initialize the Bot info, Redis client, and last.fm connection"""
        self.nickname = nickname
        self.chans = chans
        self.factory = fact
        self.db = Contacts()
        self.youtube = Youtube()
        self.commands = Commands(self)
        self.last = pylast.LastFMNetwork(api_key=secrets.API_KEY,
                                         api_secret=secrets.API_SECRET,
                                         username=secrets.username,
                                         password_hash=secrets.password_hash)

    def _isPrivate(self, nick, channel):
        """sets the private context based on channel or user"""
        return (channel == self.nickname and nick != self.nickname)

    def signedOn(self):
        for chan in self.chans:
            self.join(chan)

    def msg(self, contact, message):
        """wraps self.msg to delegate the reply"""
        channel = contact.nick if contact.private else contact.channel
        irc.IRCClient.msg(self, channel, message)

    def privmsg(self, user, channel, message):
        """manages contacts based on message and dispatches it to Commands

        Interface with Redis for getting, or creating, the Contact and setting
        its context, then passing it off to be parsed.
        """
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

        # only respond if it's properly said
        if contact.private or message.startswith("!"):
            self.commands.parse(contact, message)


class BotFactory(ReconnectingClientFactory):
    """factory for Bots, with reconnection action"""

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
    # start the Redis server
    from subprocess import call
    call(["redis-server", "redis.conf"])

    # set IRC info for Bot connections
    server = "irc.cat.pdx.edu"
    port = 6697
    nickname = "last"
    channels = ["Music", "#botgrounds"]
    factory = BotFactory(nickname, channels)

    # start it
    reactor.connectSSL(server, port, factory, ssl.ClientContextFactory())
    reactor.run()
