from bs4 import BeautifulSoup
from tors import TorProc
from time import sleep
from random import random

def get_timestamp_of_post(post):
    tag = post.find('span', {'class': '_timestamp'})
    if tag is None:
        return None
    if not tag.attrs.has_key('data-time-ms'):
        return None
    time = tag.attrs['data-time-ms']
    return time


class FeedAccumulator:
    def __init__(self):
        self.posts = []

    def addUser(self, user):
        src = TorProc.random().get("https://twitter.com/" + str(user))
        soup = BeautifulSoup(src)
        posts = soup.findAll('li', {'class': 'stream-item'})
        self.posts += posts

    def getFeed(self):
        return sorted(self.posts, key=get_timestamp_of_post)

    @staticmethod
    def interleave(users, maxtimeout=6):
        fa = FeedAccumulator()
        for user in users:
            sleep(random() * maxtimeout)
            fa.addUser(user)
        return fa.getFeed()
