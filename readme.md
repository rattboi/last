# last replacement for #music using [pylast](http://code.google.com/p/pylast/), [redis](http://redis.io/), and [twisted](http://twistedmatrix.com/trac/)

### Modified to deploy to Heroku

## Heroku Configuration

You need to set up a few heroku config options:

You need a redis instance to store the IRC/Last.fm username mappings. You can use a free redistogo heroku addon for this.

`heroku addons:add redistogo`

## Last-bot configuration

You need to set the following environment variables:

|IRC connection info|                                                                                               |
|-------------------|-----------------------------------------------------------------------------------------------|
| IRC_SERVER        | IRC Server to connect to                                                                      |
| IRC_PORT          | IRC Server's port                                                                             |
| IRC_NICK          | Bot's IRC Nickname                                                                            |
| IRC_CHANS         | Comma-separated list of channels to join (e.g. heroku config:set IRC_CHANS=#Music,#Testing)   |

| Last.fm info      |                                                                                               |
|-------------------|-----------------------------------------------------------------------------------------------|
| LAST_API_KEY      | Last.fm's API key                                                                             |
| LAST_API_SECRET   | Last.fm's API secret                                                                          |
| LAST_USER         | Last.fm username                                                                              |
| LAST_PASS_HASH    | Last.fm password                                                                              |

| Yout API info     |                                                                                               |
|-------------------|-----------------------------------------------------------------------------------------------|
| YOUTUBE_API_KEY   | Youtube Developer API key                                                                     |
