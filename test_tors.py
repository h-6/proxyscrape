import os
from random import choice, shuffle, random
from time import sleep

cmd_template = "curl --socks5-hostname localhost:{socksport} 'http://ifconfig.co/ip'"

set_socksport = xrange(9051,9149)

for socksport in set_socksport:
    os.system(cmd_template.format(socksport=socksport))
