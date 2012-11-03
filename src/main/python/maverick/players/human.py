#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

#import os
#import sys

from ..client import MaverickClient


###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################


def main(host, port):
    nc = MaverickClient(host, port)
    nc.register("FooBar")

if __name__ == '__main__':
    main()
