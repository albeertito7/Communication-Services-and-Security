import sys
import argparse, os
from argparse import RawTextHelpFormatter
from functools import partial

# global vars
VERBOSE = DISPLAY = False
ALGORITHM_CHOICES = ('FQ', 'WFQ')

def parse_arguments():
    parser = argparse.ArgumentParser(prog="Network Scheduling Script", description="Script implementing a packet-based network scheduling algorithm called Fair Queueing and its Weighted version.", formatter_class=RawTextHelpFormatter)

    # Required Arguments
    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File name containing the list of triplets to be scheduled.')
    
    # Optional Arguments
    parser.add_argument('-s', dest="type", type=str, default="FQ", choices=ALGORITHM_CHOICES, required=False, help="String to specify the network scheduling algorithm policy. If not specified will be executed the Fair Queueing as a default option.\n  · FQ = Fair Queueing\n  · WFQ = Weighted Fair Queueing.\n")
    parser.add_argument('-f', dest="flows", type=str, required=False, help='Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40 \nWill only be taken into account when the policy {WFQ} is specified.')
    parser.add_argument('-o', dest='outFile', type=str, required=False, help='Output file name containing the results')
    parser.add_argument('-v', dest='verbose', action='store_true', default=False, required=False, help='Display additional details about the execution such as the packets received and delivered at each time.')
    #parser.add_argument('-d', dest="display", action='store_true', default=False, required=False, help='Display results on the screen')

    return parser.parse_intermixed_args()

def is_file(parser, file):
    if not os.path.isfile(file): parser.error("File path '{}' does not exist. Exiting...".format(file))
    return open(file, 'r')

def errorHandler():
    return "Error: scheduler mechanism not specified"

def schedule(data, flows=None, type="FQ"):
    return {
        "FQ": partial(fair_queueing, data),
        "WFQ": partial(weighted_fair_queueing, data, flows)
    }.get(type, errorHandler)()

def fair_queueing(data, timeFinish=0, packets_received=[], packets_delivered=[]):
    
    if len(data) <= 0 and len(packets_received) <= 0: # terminal test
        return packets_delivered

    count_adds = 0

    for packet in data:
        if packet[1] <= timeFinish:
            time_estimated = max(timeFinish, packet[1]) + packet[2]
            packets_received.append(packet+[time_estimated]) # packets received at a time
            count_adds += 1

    if(len(packets_received) <= 0 and count_adds == 0):
        timeFinish = data[0][1]
        for packet in data:
            if packet[1] <= timeFinish:
                time_estimated = max(timeFinish, packet[1]) + packet[2]
                packets_received.append(packet+[time_estimated]) # packets received at a time
                count_adds += 1

    data = data[count_adds:] # remove packets received

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

    count_adds = 0

    for packet in data:
        if packet[1] <= timeFinish:
            time_estimated = max(timeFinish, packet[1]) + packet[2]*flows[int(packet[3])-1]
            packets_received.append(packet+[time_estimated]) # packets received at a time
            count_adds += 1

    if(len(packets_received) <= 0 and count_adds == 0):
        timeFinish = data[0][1]
        for packet in data:
            if packet[1] <= timeFinish:
                time_estimated = max(timeFinish, packet[1]) + packet[2]*flows[int(packet[3])-1]
                packets_received.append(packet+[time_estimated]) # packets received at a time
                count_adds += 1

    data = data[count_adds:] # remove packets received
    
    if VERBOSE: print("Data to receive: ", data, "\nReceived packets: ", packets_received)

    packet_to_deliver = min(packets_received, key=lambda x: x[4])

    timeFinish+=packet_to_deliver[2] # size sum
    packets_received.remove(packet_to_deliver) # remove first occurrence
    packets_delivered.append(packet_to_deliver+[timeFinish]) # packet with less time sent
    
    if VERBOSE: print("Packet delivered: ", packet_to_deliver+[timeFinish]), print('-' * os.get_terminal_size().columns)

    return weighted_fair_queueing(data, flows, timeFinish, packets_received, packets_delivered)

def printResult(data): 
    print("Result: ", [x[0] for x in data])

def main():
    args = parse_arguments() # parse arguments

    global VERBOSE
    VERBOSE = args.verbose

    data = [list(map(float, [num] + line.strip().split())) for num, line in enumerate(args.file.readlines(), 1)]
    flows = [x/100 for x in list(map(float, args.flows.split(",")))] if args.flows and args.type == ALGORITHM_CHOICES[1] else None

    result = schedule(data, flows, type=args.type)
    printResult(result)

if __name__ == '__main__':
    main()