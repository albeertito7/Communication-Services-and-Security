import sys
import argparse, os

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=lambda x: is_file(parser, x), help='File name containing the list of triplets to be scheduled.')
    parser.add_argument('flows', type=str, help='Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40')
    parser.add_argument('outFile', type=str, nargs="?", default="outWFQ", help='Output file name containing the results')
    parser.add_argument('-d', '--display', action='store_true', required=False, help='Display results on the screen')

    return parser.parse_intermixed_args()

def is_file(parser, file):
    if not os.path.isfile(file):
        parser_error("File path '{}' does not exist. Exiting...".format(file))
    else:
        return open(file, 'r')

def main():
    args = parse_arguments()

    data = list()
    [data.append(tuple(line.strip().split(" "))) for line in args.file.readlines()]

    flows = list(map(int, args.flows.split(",")))

    print(data)
    print(flows)

if __name__ == '__main__':
    main()