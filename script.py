import sys
import os

def main():
    file = sys.argv[1]

    if not os.path.isfile(file):
       print("File path {} does not exist. Exiting...".format(file))
       sys.exit(-1)

    list = []
    with open(file) as file_in:
        for line in file_in:
            list.append(tuple(line.strip().split(" ")))

    print(list)


if __name__ == '__main__':
    main()