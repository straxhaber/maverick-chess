#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

#import os
#import sys

from client import MaverickClient


###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################


def main(host='127.0.0.1', port='7782'):
    nc = MaverickClient(host, port)
    playerID = nc.register("FooBar")
    gameID = nc.joinGame(playerID)
    status = nc.getStatus(gameID)
    #state = nc.getState(playerID, gameID)
    print playerID
    print status


if __name__ == '__main__':
    main()
