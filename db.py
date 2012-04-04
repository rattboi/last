# redis backend for username persistence

import cPickle
from redis import Redis

class Contacts(dict):

    def __init__(self):
        self.redis = Redis(host="localhost", port=6379, db=0)
        self.save = self.redis.save

    def get(self, username):
        if self.redis.exists(username):
            return cPickle.loads(self.redis.get(username))
        else:
            return None

    def set(self, username, contact):
        return self.redis.set(username,
                              cPickle.dumps(contact, cPickle.HIGHEST_PROTOCOL))
