import sys
import argparse, os
from operator import itemgetter
from argparse import RawTextHelpFormatter
from functools import partial

# global vars
VERBOSE = False

def parse_arguments():
    parser = argparse.ArgumentParser(prog="Network Scheduling Script", description="Script implementing a packet-based network scheduling algorithm called Weighted Fair Queueing.", formatter_class=RawTextHelpFormatter)

    # Required Arguments
    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File path name containing the list of triplets to be scheduled where each one represents:\n'
        '   1. Arrival time (float)\n'
        '   2. Packet length (float)\n'
        '   3. Flow/Stream identifier (integer >= 1)')
    parser.add_argument('flows', type=str, help='Fraction of the bandwidth assigned to each flow (as a percentage)(float). Comma separated. As an example: 50,10,40')

    # Optional Arguments
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, required=False, help='Display additional details about the execution such as the packets received and delivered at each time.')

    args = parser.parse_intermixed_args()

    global VERBOSE
    VERBOSE = args.verbose

    data = [list(map(float, [num] + line.strip().split())) for num, line in enumerate(args.file.readlines(), 1)] # data read
    flows = [x*0.01 for x in list(map(float, args.flows.split(",")))] if args.flows else None # flows read

    if len(set(map(itemgetter(3), data))) != len(flows): # checking number flows consistency
        parser.error("The number of flows are not consistent with the arguments done.")

    return type('obj', (object,), {
        'data': data,
        'flows': flows
    })

# is file check, and open
def is_file(parser, file):
    if not os.path.isfile(file): parser.error("File path '{}' does not exist. Exiting...".format(file))
    return open(file, 'r')

def weighted_fair_queueing(data, flows, time_upper_thld=0, packets_received=[], packets_sent=[]):

    if len(data) <= 0 and len(packets_received) <= 0: # terminal test
        return packets_sent

    filtered = list(filter(lambda packet: packet[1] <= time_upper_thld, data)) # filter data by time upper threshold

    if len(filtered) == 0:
        filtered = list(filter(lambda packet: packet[1] <= data[0][1], data))

    [packets_received.append(packet+[max(time_upper_thld, packet[1]) + packet[2]*flows[int(packet[3])-1]]) for packet in filtered] # for each new received packet, apply WFQ calculation

    data = data[len(filtered):] # remove packets received
    
    if VERBOSE: print("Data to receive: ", data, "\nReceived packets: ", packets_received) # print data, and received packets at each time

    packet_to_deliver = min(packets_received, key=lambda x: x[4])

    time_upper_thld+=packet_to_deliver[2] # size sum
    packets_received.remove(packet_to_deliver) # remove first occurrence
    packets_sent.append(packet_to_deliver+[time_upper_thld]) # packet with less time sent
    
    if VERBOSE: print("Packet sent: ", packet_to_deliver+[time_upper_thld]), print('-' * os.get_terminal_size().columns) # print packets sent at each time

    return weighted_fair_queueing(data, flows, time_upper_thld, packets_received, packets_sent)

def errorHandler():
    return "Error: scheduler mechanism not specified"

def schedule(data, flows=None, type="WFQ"): # switcher which contain all algorithms implemented
    return {
        #"FQ": partial(fair_queueing, data),
        "WFQ": partial(weighted_fair_queueing, data, flows)
    }.get(type, errorHandler)()

def printResult(data): 
    print("Result: ", [int(x[0]) for x in data])

def main():
    args = parse_arguments() # parse arguments

    result = schedule(args.data, args.flows)
    printResult(result)

if __name__ == '__main__':
    main()