#!/usr/bin/python

"""TODO.py: TODO write a description"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

#from maverick-chess.client.MaverickTelnetClient import MaverickClient
from client.MaverickTelnetClient import MaverickClient


class FooAI(MaverickClient):
    """TODO"""

    def runAI(self):
        pass  # TODO


def main():
    FooAI().runAI()

if __name__ == '__main__':
    main()
