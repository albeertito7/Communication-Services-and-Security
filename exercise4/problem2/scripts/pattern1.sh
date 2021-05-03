#!/bin/bash

# ICT Project: Communication Services and Security
# Exercise 4 Problem 2 Pattern 1
# Albert Pérez Datsira

while true;
do
 sudo ./packETHcli -i tap0 -d 6000 -m 2 -f ping-1000-tap0.pcap -t 1;
 sleep 1;
done;


# pattern 2
# sudo ./packETHcli -i tap0 -d 9100 -n 0 -m 2 -f udp-size_1356-port_dest_5004_ip_13.0.0.1.pcap

# pattern 3
# sudo ./packETHcli -i tap1 -d 9800 -n 0 -m 2 -f udp-size_1356-port_dest_5004_ip_13.0.0.1.pcap