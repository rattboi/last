# last replacement for #music

from twisted.internet import ssl, reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.words.protocols import irc
from commands import Commands


class Contact(object):

    def __init__(self, user, channel):
        self.user = user
        self.channel = channel
        self.nick = self._nick(user)
        self.lastname = None
        self.private = False

    def _nick(self, user):
        return user.split('!', 1)[0]

    def setLastName(self, lastname):
        self.lastname = lastname


class Bot(irc.IRCClient):

    def __init__(self, nickname, chans, fact):
        self.nickname = nickname
        self.chans = chans
        self.factory = fact
        self.contacts = {}
        self.commands = Commands(self)

    def _isPrivate(self, nick, channel):
        return (channel == self.nickname and nick != self.nickname)

    def signedOn(self):
        for chan in self.chans:
            self.join(chan)

    def msg(self, contact, message):
        channel = contact.nick if contact.private else contact.channel
        irc.IRCClient.msg(self, channel, message)

    def privmsg(self, user, channel, message):
        contact = self.contacts.get(user, None)

        # update private context for replies to existing contact
        if contact:
            private = self._isPrivate(contact.nick, channel)
            if contact.private != private:
                contact.channel = channel
            contact.private = self.contacts[contact.user].private = private
        # if new contact, create and set private context
        else:
            contact = Contact(user, channel)
            contact.private = self._isPrivate(contact.nick, channel)
            self.contacts[contact.user] = contact

        if contact.private or message.startswith("$"):
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
    server = "irc.cat.pdx.edu"
    port = 6697
    nickname = "last"
    channels = ["#botgrounds"]
    factory = BotFactory(nickname, channels)
    reactor.connectSSL(server, port, factory, ssl.ClientContextFactory())
    reactor.run()
