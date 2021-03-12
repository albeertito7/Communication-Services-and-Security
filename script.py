import sys
import os

def main():
    file = sys.argv[1]
    flows = list(map(int, sys.argv[0].split(",")))

    if not os.path.isfile(file):
       print("File path {} does not exist. Exiting...".format(file))
       sys.exit(-1)
       
    list = []
    with open(file) as reader: [list.append(tuple(line.strip().split(" "))) for line in reader]

    print(list)
    print(flows)


if __name__ == '__main__':
    main()