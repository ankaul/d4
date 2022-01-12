#!/usr/bin/python

import subprocess
import sys
import os

CID = int(sys.argv[1])
SCENARIO = sys.argv[2]


def check_key(filename, cid):
    cmd = "md5sum %s-c%s.pem" % (filename, cid)
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    return out.decode().split(' ')[0]


if __name__ == '__main__':

    filename = 'public_key_x'
    if 'd' in SCENARIO[-1:]:
        filename = 'public_key'

    my_hash = check_key(filename, CID)
    agree = []

    for cid in range(0, 3):
        if CID != cid:
            hash_ = check_key(filename, cid)
            if my_hash == hash_:
                agree.append('%s-agreed' % cid)
            else:
                agree.append('%s-no' % cid)

    os.system('mosquitto_pub -h 192.168.0.1 -t c%s -m \"c%s,c%s\" -r' % (CID, agree[0], agree[1]))
