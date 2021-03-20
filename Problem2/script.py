import sys
import argparse, os
from operator import itemgetter
from functools import partial

# global vars
VERBOSE = False

def parse_arguments():
    parser = argparse.ArgumentParser(prog="Network Scheduling Script", description="Script implementing a packet-based network scheduling algorithm called Weighted Fair Queueing.")

    # Required Arguments
    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File name containing the list of triplets to be scheduled.')
    parser.add_argument('flows', type=str, help='Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40')

    # Optional Arguments
    parser.add_argument('-v', dest='verbose', action='store_true', default=False, required=False, help='Display additional details about the execution such as the packets received and delivered at each time.')

    args = parser.parse_intermixed_args()

    global VERBOSE
    VERBOSE = args.verbose

    data = [list(map(float, [num] + line.strip().split())) for num, line in enumerate(args.file.readlines(), 1)]
    flows = [x*0.01 for x in list(map(float, args.flows.split(",")))] if args.flows else None

    if len(set(map(itemgetter(3), data))) != len(flows):
        parser.error("The number of flows are not consistent with the arguments done.")

    return type('obj', (object,), {
        'data': data,
        'flows': flows
    })

def is_file(parser, file):
    if not os.path.isfile(file): parser.error("File path '{}' does not exist. Exiting...".format(file))
    return open(file, 'r')

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

def printResult(data): 
    print("Result: ", [x[0] for x in data])

def errorHandler():
    return "Error: scheduler mechanism not specified"

def schedule(data, flows=None, type="WFQ"):
    return {
        #"FQ": partial(fair_queueing, data),
        "WFQ": partial(weighted_fair_queueing, data, flows)
    }.get(type, errorHandler)()

def main():
    args = parse_arguments() # parse arguments

    result = schedule(args.data, args.flows)
    printResult(result)

if __name__ == '__main__':
    main()