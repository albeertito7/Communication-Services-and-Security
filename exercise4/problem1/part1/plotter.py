#!/usr/bin/python


import pylab as pl
import numpy as np
from pylab import *
from numpy import ma
import re
import csv;


def ReadData(filename,c):
    global time, rate;

    with open(filename, 'rb') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        mediumRate = 0
        totalrows = 0
        
        for row in spamreader:
            time[c].append(float(row['time']))
            rate[c].append(float(row['rate']))
            totalrows += 1
            mediumRate += float(row['rate'])
            
        mediumRate = mediumRate / totalrows
        print(filename, mediumRate)


def Plot():
    pl.figure(figsize=(18, 10), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(time[0], rate[0], linewidth=1, color='blue', label='Without Traffic Shaping')
    pl.plot(time[1], rate[1], linewidth=1, color='red', label='Traffic Shaping rate 200 kB/s')
    pl.plot(time[2], rate[2], linewidth=1, color='green', label='Traffic Shaping rate 800 kB/s')
    pl.plot(time[3], rate[3], linewidth=1, color='yellow', label='Traffic Shaping rate 1000 kB/s')


    pl.legend()
    pl.ylabel('rate Bytes/second')
    pl.xlabel('Seconds')
    pl.yticks(np.arange(0,230000,10000))
    pl.xticks(np.arange(0,180,10))
    pl.grid()
    pl.savefig("traffic.png")
    pl.show()


time = []
time.append([])
time.append([])
time.append([])
time.append([])

rate = []
rate.append([])
rate.append([])
rate.append([])
rate.append([])


ReadData('./without_traffic.csv',0);
ReadData('./200.csv',1);
ReadData('./800.csv',2);
ReadData('./1000.csv',3);


Plot()
