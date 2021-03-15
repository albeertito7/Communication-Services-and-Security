import sys
import argparse, os

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File name containing the list of triplets to be scheduled.')
    parser.add_argument('flows', type=str, help='Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40')
    parser.add_argument('outFile', type=str, nargs="?", default="outWFQ", help='Output file name containing the results')
    # parser.add_argument('-d', '--display', action='store_true', required=False, help='Display results on the screen')

    return parser.parse_intermixed_args()

def is_file(parser, file):
    if not os.path.isfile(file):
        parser_error("File path '{}' does not exist. Exiting...".format(file))
    else:
        return open(file, 'r')

def main():
    args = parse_arguments()

    data = [list(map(float, line.strip().split())) for line in args.file.readlines()]
    flows = [x/100 for x in list(map(int, args.flows.split(",")))]

    print("Flows: ", flows)

    result = schedule(data, flows, type="WFQ")
    printResult(result)

def schedule(data, flows, type):
    return {
        "FQ": fair_queueing(data),
        "WFQ": weighted_fair_queueing(data, flows)
    }.get(type, "Error: scheduler mechanism not specified")
    
def fair_queueing(data, timeFinish=0, packets_received=[], packets_delivered=[]):
        
    if len(data) <= 0 and len(packets_received) <= 0:
        return packets_delivered

    count_adds = 0

    for packet in data:
        if packet[0] <= timeFinish:
            time_estimated = max(timeFinish, packet[0]) + packet[1]
            packets_received.append(packet+[time_estimated]) # packets received at a time
            count_adds += 1

    if(len(packets_received) <= 0 and count_adds == 0):
        timeFinish = data[0][0]
        for packet in data:
            if packet[0] <= timeFinish:
                time_estimated = max(timeFinish, packet[0]) + packet[1]
                packets_received.append(packet+[time_estimated]) # packets received at a time
                count_adds += 1

    data = data[count_adds:] # remove packets received
    print("Data to receive: ", data)
    print("Received packets: ", packets_received)

    tmp = packets_received[0][3]
    packet_less = packets_received[0]
    for less in packets_received:
        if less[3] < tmp:
            tmp = less[3]
            packet_less = less

    timeFinish+=packet_less[1] # size sum

    packets_received.remove(packet_less) # remove first occurrence
    packets_delivered.append(packet_less+[timeFinish]) # packet with less time sent
    
    print("Packet delivered: ", packet_less+[timeFinish])
    print("-------------------------------------------------------------------------------------------------------------------------------------------------")

    return fair_queueing(data, timeFinish, packets_received, packets_delivered)


def weighted_fair_queueing(data, flows, timeFinish=0, packets_received=[], packets_delivered=[]):
    if len(data) <= 0 and len(packets_received) <= 0:
        return packets_delivered

    count_adds = 0

    for packet in data:
        if packet[0] <= timeFinish:
            time_estimated = max(timeFinish, packet[0]) + packet[1]*flows[int(packet[2])-1]
            packets_received.append(packet+[time_estimated]) # packets received at a time
            count_adds += 1

    if(len(packets_received) <= 0 and count_adds == 0):
        timeFinish = data[0][0]
        for packet in data:
            if packet[0] <= timeFinish:
                time_estimated = max(timeFinish, packet[0]) + packet[1]*flows[int(packet[2])-1]
                packets_received.append(packet+[time_estimated]) # packets received at a time
                count_adds += 1

    data = data[count_adds:] # remove packets received
    print("Data to receive: ", data)
    print("Received packets: ", packets_received)

    tmp = packets_received[0][3]
    packet_less = packets_received[0]
    for less in packets_received:
        if less[3] < tmp:
            tmp = less[3]
            packet_less = less

    timeFinish+=packet_less[1] # size sum

    packets_received.remove(packet_less) # remove first occurrence
    packets_delivered.append(packet_less+[timeFinish]) # packet with less time sent
    
    print("Packet delivered: ", packet_less+[timeFinish])
    print("-------------------------------------------------------------------------------------------------------------------------------------------------")

    return weighted_fair_queueing(data, flows, timeFinish, packets_received, packets_delivered)

def printResult(data):
    pass

if __name__ == '__main__':
    main()