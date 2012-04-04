# redis backend for username persistence

import cPickle
from redis import Redis

class Contacts(dict):
    """Redis backend to make IRC Contacts persistent

    This wraps Redis to pickle Contacts, using the hostmasks as keys.
    """

    def __init__(self):
        """start the Redis client"""
        self.redis = Redis(host="localhost", port=6379, db=0)
        self.save = self.redis.save

    def get(self, username):
        """return a contact for a user, failing silently"""
        if self.redis.exists(username):
            return cPickle.loads(self.redis.get(username))
        else:
            return None

    def set(self, username, contact):
        """pickle and store Contact"""
        return self.redis.set(username,
                              cPickle.dumps(contact, cPickle.HIGHEST_PROTOCOL))
