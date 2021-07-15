"""
ICT Project: Communication Services and Security
Exercise 4 Problem 1 Part 2
Albert Pérez Datsira
"""

import sys
import argparse, os
from argparse import RawTextHelpFormatter

def parse_arguments():
	parser = argparse.ArgumentParser(prog="Packet loss counter", description="Script that counts from the transmission ffplay log file, the packets lost.", formatter_class=RawTextHelpFormatter)

	# Required Arguments
	parser.add_argument('file', type=lambda x: is_valid(parser, x), help='File path name containing the log.txt from the a corresponding ffplay streaming.')

	return parser.parse_intermixed_args()

# is file check, and open
def is_valid(parser, file):
	if not os.path.isfile(file):
		parser.error("File path '{}' does not exist. Exiting...".format(file))
	elif os.path.splitext(file)[1] != ".txt":
		parser.error("File '{}' is not a log with '.txt' extension. Exiting...".format(file))
	return open(file, 'r')

def main():
	args = parse_arguments()

	counter = 0
	for line in args.file.readlines():
		if line.__contains__('RTP'):
			counter += int(line.split()[5])
			
	print('Packets lost: %s' % counter)

if __name__ == '__main__':
    main()