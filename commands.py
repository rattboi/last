# where the magic happens

from pylast import User


class Commands(object):

    def __init__(self, bot):
        self.bot = bot
        self.commands = "all start with '!': l, lp, set <username>, help"

    def _decode(self, track=None, artist=None):
        if type(track) is unicode:
            track = track.encode("utf-8")
        if type(artist) is unicode:
            artist = artist.encode("utf-8")
        return track, artist

    def _last_wrap(cmd):
        def api_tries(self, contact, msg):
            try:
                now = contact.last.get_now_playing()
                if now is not None:
                    reply = "now playing: "
                else:
                    now = contact.last.get_recent_tracks(limit=1)[0].track
                    reply = "last played: "
            except AttributeError:
                reply = "username for %s not set, use !set" % contact.nick
            else:
                try:
                    reply += cmd(self, now, msg)
                except AttributeError:
                    reply = "no track info found"
            self.bot.msg(contact, reply)
        return api_tries

    @_last_wrap
    def command_l(self, now, args):
        """shows now playing"""
        track = now.get_name()
        artist = now.get_artist().get_name()
        track, artist = self._decode(track=track, artist=artist)
        return "'%s' by %s" % (track, artist)

    @_last_wrap
    def command_lp(self, now, args):
        """karma's now playing"""
        artist = now.get_artist().get_name()
        _, artist = self._decode(artist=artist)
        if len(artist.split()) > 1:
            artist = "(%s)" % artist
        return "%s++" % artist

    def command_set(self, contact, args):
        """sets <username> for nick"""
        if len(args.split()) > 1:
            self.bot.msg(contact, "found too many args, only need <username>")
            return
        contact.setLastUser(User(args, self.bot.last))
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
