# where the magic happens

import simplejson as json


class Commands(object):

    def __init__(self, bot):
        self.bot = bot
        self.commands = "all start with '!': l, lp, set <username>, help"

    def command_l(self, contact, args):
        """!l - shows now playing"""
        self.bot.msg(contact, "in !l")

    def command_lp(self, contact, args):
        """!lp - karma's now playing"""
        self.bot.msg(contact, "in !lp")

    def command_set(self, contact, args):
        """!set <username> - sets <username> for nick"""
        self.bot.msg(contact, "in !set %s" % args)

    def command_help(self, contact, args):
        """!help - display help"""
        args = args.split()
        if not args:
            self.bot.msg(contact, self.commands)
        else:
            cmd = args[0]
            try:
                cmd_help = getattr(self, "command_" + cmd.lower()).__doc__
                self.bot.msg(contact, "%s: %s" % (cmd, cmd_help))
            except AttributeError:
                self.bot.msg(contact,
                             "%s isn't a command, try '!help'" % cmd)

    def parse(self, contact, msg):
        if msg.startswith("$"):
            msg = msg[1:]
        cmd, _, args = msg.partition(" ")

        try:
            meth = getattr(self, "command_" + cmd.lower())
            return meth(contact, args)
        except AttributeError:
            self.bot.msg(contact, "%s isn't a command, try '!help'" % cmd)
