"""
ICT Project: Communication Services and Security
Exercise 1
Albert Pérez Datsira
"""

import sys
import argparse, os
from argparse import RawTextHelpFormatter
from operator import itemgetter
from functools import partial

# global vars
VERBOSE = DISPLAY = False
ALGORITHM_CHOICES = ('FQ', 'WFQ') # possible algorithms

def parse_arguments(): # specific arguments parser
    parser = argparse.ArgumentParser(prog="Network Scheduling Script", description="Script implementing a packet-based network scheduling algorithm called Fair Queueing and its Weighted version. Also it is prepared to manage other network scheduling algorithms.", formatter_class=RawTextHelpFormatter)

    # Required Arguments
    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File path name containing the list of triplets to be scheduled where each one represents:\n'
        '   1. Arrival time (float)\n'
        '   2. Packet length (float)\n'
        '   3. Flow/Stream identifier (integer >= 1)')
    
    # Optional Arguments
    parser.add_argument('-s', dest="type", type=str, default="FQ", choices=ALGORITHM_CHOICES, required=False, help="String to specify the network scheduling algorithm policy. If not specified will be executed the Fair Queueing as a default option.\n  · FQ = Fair Queueing\n  · WFQ = Weighted Fair Queueing.\n")
    parser.add_argument('-f', dest="flows", type=str, required=False, help='Fraction of the bandwidth assigned to each flow (as a percentage)(float). Comma separated. As an example: 50,10,40 \nWill only be taken into account when the policy {WFQ} is specified.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, required=False, help='Display additional details about the execution such as the packets received and delivered at each time.')
    #parser.add_argument('-o', dest='outFile', type=str, required=False, help='Output file name containing the results')
    #parser.add_argument('-d', dest="display", action='store_true', default=False, required=False, help='Display results on the screen')

    args = parser.parse_intermixed_args()

    global VERBOSE
    VERBOSE = args.verbose

    data = [list(map(float, [num] + line.strip().split())) for num, line in enumerate(args.file.readlines(), 1)]
    flows = [x*0.01 for x in list(map(float, args.flows.split(",")))] if args.flows and args.type == ALGORITHM_CHOICES[1] else None

    if args.type == args.type == ALGORITHM_CHOICES[1] and len(set(map(itemgetter(3), data))) != len(flows):
        parser.error("The number of flows are not consistent with the arguments done.")

    return type('obj', (object,), {
        'data': data,
        'flows': flows,
        'type': args.type
    })


def is_file(parser, file):
    if not os.path.isfile(file): parser.error("File path '{}' does not exist. Exiting...".format(file))
    return open(file, 'r')

def fair_queueing(data, timeFinish=0, packets_received=[], packets_delivered=[]):
    
    if len(data) <= 0 and len(packets_received) <= 0: # terminal test
        return packets_delivered

    filtered = list(filter(lambda packet: packet[1] <= timeFinish, data))

    if len(filtered) == 0:
        filtered = list(filter(lambda packet: packet[1] <= data[0][1], data))

    [packets_received.append(packet+[max(timeFinish, packet[1]) + packet[2]]) for packet in filtered]

    data = data[len(filtered):] # remove packets received

    if VERBOSE: print("Data to receive: ", data, "\nReceived packets: ", packets_received)

    packet_to_deliver = min(packets_received, key=lambda x: x[4])

    timeFinish+=packet_to_deliver[2]
    packets_received.remove(packet_to_deliver) # remove first occurrence
    packets_delivered.append(packet_to_deliver+[timeFinish]) # packet with less time sent
 
    if VERBOSE: print("Packet delivered: ", packet_to_deliver+[timeFinish]), print('-' * os.get_terminal_size().columns)

    return fair_queueing(data, timeFinish, packets_received, packets_delivered)

def weighted_fair_queueing(data, flows, timeFinish=0, packets_received=[], packets_delivered=[]):

    if len(data) <= 0 and len(packets_received) <= 0:
        return packets_delivered

    filtered = list(filter(lambda packet: packet[1] <= timeFinish, data))

    if len(filtered) == 0:
        filtered = list(filter(lambda packet: packet[1] <= data[0][1], data))

    [packets_received.append(packet+[max(timeFinish, packet[1]) + packet[2]*flows[int(packet[3])-1]]) for packet in filtered]

    data = data[len(filtered):] # remove packets received
    
    if VERBOSE: print("Data to receive: ", data, "\nReceived packets: ", packets_received)

    packet_to_deliver = min(packets_received, key=lambda x: x[4])

    timeFinish+=packet_to_deliver[2] # size sum
    packets_received.remove(packet_to_deliver) # remove first occurrence
    packets_delivered.append(packet_to_deliver+[timeFinish]) # packet with less time sent
    
    if VERBOSE: print("Packet delivered: ", packet_to_deliver+[timeFinish]), print('-' * os.get_terminal_size().columns)

    return weighted_fair_queueing(data, flows, timeFinish, packets_received, packets_delivered)
    
def errorHandler():
    return "Error: scheduler mechanism not specified"

def schedule(data, flows=None, type="FQ"): # switcher to scale the script
    return {
        "FQ": partial(fair_queueing, data), # fair queueing algorithm
        "WFQ": partial(weighted_fair_queueing, data, flows) # weighted fair queueing algorithm
    }.get(type, errorHandler)()

def printResult(data): 
    print("Result: ", [int(x[0]) for x in data])

def main():
    args = parse_arguments() # parse arguments

    result = schedule(args.data, args.flows, args.type)
    printResult(result)

if __name__ == '__main__':
    main()