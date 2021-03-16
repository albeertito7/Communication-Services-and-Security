import sys
import argparse, os
from argparse import RawTextHelpFormatter
from functools import partial

VERBOSE = False

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script implementing a packet-based network scheduling algorithm called Fair Queueing and its Weighted version.", formatter_class=RawTextHelpFormatter)

    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File name containing the list of triplets to be scheduled.')
    parser.add_argument('-s', dest="type", default="FQ", choices=['FQ', 'WFQ'], type=str, required=False, help="String to specify the network scheduling algorithm policy. If not specified will be executed the Fair Queueing as a default option.\n"
        "   · FQ = Fair Queueing\n"
        "   · WFQ = Weighted Fair Queueing.\n")
    parser.add_argument('-f', dest="flows", type=str, required=False, help='Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40 \nWill only be taken into account when the policy {WFQ} is specified.')
    parser.add_argument('-o', dest='outFile', type=str, required=False, help='Output file name containing the results')
    parser.add_argument('-v', dest='verbose', default=False, action='store_true', required=False, help='Display additional details about the execution such as the packets received and delivered at each time.')
    #parser.add_argument('-d', action='store_true', required=False, help='Display results on the screen')

    return parser.parse_intermixed_args()

def is_file(parser, file):
    if not os.path.isfile(file):
        parser_error("File path '{}' does not exist. Exiting...".format(file))
    else:
        return open(file, 'r')

def main():
    args = parse_arguments()

    VERBOSE = args.verbose

    #data = [list(map(float, line.strip().split())) for line in args.file.readlines()]

    #flows = [x/100 for x in list(map(float, args.flows.split(",")))]

    print("Scheduler: ", args.type)
    print("Flows: ", args.flows)
    print("Output file: ", args.outFile)
    print("Verbose: ", VERBOSE)

    #result = schedule(data, flows, type=args.type)
    #printResult(result)

def schedule(data, flows=None, type="FQ"):
    switcher = {
        "FQ": partial(fair_queueing, data),
        "WFQ": partial(weighted_fair_queueing, data, flows)
    }
    return switcher.get(type, errorHandler)()
    
def errorHandler():
    return "Error: scheduler mechanism not specified"

def fair_queueing(data, timeFinish=0, packets_received=[], packets_delivered=[]):
    
    if len(data) <= 0 and len(packets_received) <= 0:
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
    
    if VERBOSE:
        print("Data to receive: ", data)
        print("Received packets: ", packets_received)

    tmp = packets_received[0][4]
    packet_less = packets_received[0]
    for less in packets_received:
        if less[4] < tmp:
            tmp = less[4]
            packet_less = less

    timeFinish+=packet_less[1] # size sum

    packets_received.remove(packet_less) # remove first occurrence
    packets_delivered.append(packet_less+[timeFinish]) # packet with less time sent
 
    if VERBOSE:
        print("Packet delivered: ", packet_less+[timeFinish])
        print("-------------------------------------------------------------------------------------------------------------------------------------------------")

    return fair_queueing(data, timeFinish, packets_received, packets_delivered)


def weighted_fair_queueing(data, flows, timeFinish=0, packets_received=[], packets_delivered=[]):

    if len(data) <= 0 and len(packets_received) <= 0:
        return packets_delivered

    count_adds = 0

    for packet in data:
        if packet[1] <= timeFinish:
            time_estimated = max(timeFinish, packet[1]) + packet[2]*flows[int(packet[3])-1]
            print(flows[int(packet[3])-1], time_estimated)
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
    
    if VERBOSE:
        print("Data to receive: ", data)
        print("Received packets: ", packets_received)

    tmp = packets_received[0][4]
    packet_less = packets_received[0]
    for less in packets_received:
        if less[4] < tmp:
            tmp = less[4]
            packet_less = less

    timeFinish+=packet_less[2] # size sum

    packets_received.remove(packet_less) # remove first occurrence
    packets_delivered.append(packet_less+[timeFinish]) # packet with less time sent
    
    if VERBOSE:
        print("Packet delivered: ", packet_less+[timeFinish])
        print("-------------------------------------------------------------------------------------------------------------------------------------------------")

    return weighted_fair_queueing(data, flows, timeFinish, packets_received, packets_delivered)

def printResult(data): 
    print("Result: ", [x[0] for x in data])


if __name__ == '__main__':
    main()