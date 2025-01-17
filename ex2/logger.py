"""
ICT Project: Communication Services and Security
Exercise 2
Albert Pérez Datsira
"""

import sys

class Logger(object):
    def __init__(self, fileName):
        self.terminal = sys.stdout
        self.log = open(fileName + ".txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    