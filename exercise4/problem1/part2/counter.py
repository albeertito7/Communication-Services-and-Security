import sys

if __name__ == '__main__':
    results = 0
    with open(sys.argv[1], 'r') as file:
        for line in file.readlines():
            if line.__contains__('RTP'):
                results += int(line.split(' ')[5])
        print('Results: %s' % results)
