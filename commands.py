# where the magic happens

from pylast import User


class Commands(object):

    def __init__(self, bot):
        self.bot = bot
        self.commands = "all start with '!': l, lp, set <username>, help"

    def command_l(self, contact, args):
        """shows now playing"""
        try:
            now = contact.last.get_now_playing()
            track = now.get_name()
            artist = now.get_artist().get_name()

            if type(track) is unicode:
                track = track.encode("utf-8")
            if type(artist) is unicode:
                artist = artist.encode("utf-8")

            reply = "'%s' by %s" % (track, artist)
        except AttributeError:
            self.bot.msg(contact, "username for %s not set right, use !set")
            return
        self.bot.msg(contact, reply)

    def command_lp(self, contact, args):
        """karma's now playing"""
        try:
            now = contact.last.get_now_playing()
            artist = now.get_artist().get_name()

            if type(artist) is unicode:
                artist = artist.encode("utf-8")

            if len(artist.split()) > 1:
                artist = "(%s)" % artist
            pp = "%s++" % artist
        except AttributeError:
            self.bot.msg(contact, "username for %s not set right, use !set")
            return
        self.bot.msg(contact, pp)

    def command_set(self, contact, args):
        """sets <username> for nick"""
        if len(args.split()) > 1:
            self.bot.msg(contact, "found too many args, only need <username>")
            return
        contact.last = User(args, self.bot.last)
        self.bot.msg(contact, "%s set to: %s" % (contact.nick, args))

    def command_help(self, contact, args):
        """display help"""
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
        if msg.startswith("!"):
            msg = msg[1:]
        cmd, _, args = msg.partition(" ")

        try:
            meth = getattr(self, "command_" + cmd.lower())
            return meth(contact, args)
        except AttributeError:
            self.bot.msg(contact, "%s isn't a command, try '!help'" % cmd)
