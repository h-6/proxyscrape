# Based on http://blog.databigbang.com/distributed-scraping-with-multiple-tor-circuits/

import os, urllib2, socks
from sockshandler import SocksiPyHandler
from random import choice

base_socks_port=9050
base_control_port=8118
tors_dir = 'tors'


def makedir(path):
    if not os.path.exists(path):
        os.mkdir(path)


# Create tors directory if it doesn't exist
makedir(tors_dir)


class TorProc:

    def __init__(self, port_offset):
        self.port_offset = int(port_offset)
        if not 0<=self.port_offset<1000000:
            raise Error('Invalid port_offset %s' % self.port_offset)
        self.socks_port = base_socks_port + self.port_offset
        self.control_port = base_control_port + self.port_offset
        self.path = tors_dir + "/" + str(self.port_offset)
        self.opener = None
        makedir(self.path)
        self.opener = urllib2.build_opener(
              SocksiPyHandler(socks.SOCKS5, "127.0.0.1", self.socks_port))

    def running(self):
        command = 'pgrep -a tor | grep "\--SocksPort %s "' % self.socks_port
        return not os.system(command)

    def start(self):
        if self.running():
            return False
        command = ' '.join((
          'tor',
          '--RunAsDaemon 1',
          '--CookieAuthentication 0' ,
          '--HashedControlPassword ""',
          '--ControlPort {}',
          '--PidFile tor{}.pid',
          '--SocksPort {}',
          '--DataDirectory {}')).format(
            self.control_port,
            self.port_offset,
            self.socks_port,
            self.path)
        print "Running: " + command
        os.system(command)

    @staticmethod
    def __kill__(socks_port):
        command = 'pgrep -a tor | grep "\--SocksPort %s" | cut -d" " -f1 | xargs kill' % socks_port
        os.system(command)
    
    @staticmethod
    def list():
        tors = []
        for port_offset in sorted(os.listdir(tors_dir), key=int):
            tors.append((port_offset, TorProc(port_offset).running()))
        return tors

    @staticmethod
    def purge():
        TorProc.__kill__('')
        os.system('rm -Rf %s' % tors_dir)
        makedir(tors_dir)

    def stop(self):
        if not self.running():
            return False
        TorProc.__kill__(self.socks_port)

    def get(self, url, **kwargs):
        try:
            stream = self.opener.open(url)
            return stream.read()
        except Error:
            return None

    @staticmethod
    def list_running():
        return [TorProc(proc) for proc, running in TorProc.list() if running]

    @staticmethod
    def random():
        procs = TorProc.list_running()
        if len(procs)==0:
            raise Error("No running tor processes")
        return choice(procs)
