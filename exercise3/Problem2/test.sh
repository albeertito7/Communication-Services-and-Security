#!/bin/bash

file=$1

if [ $# -eq 0 ]
then
    echo "No file argument supplied. Must be specified the .pcapng file to be evaluated."
elif [ "${file##*.}" != "pcapng" ]
then
	echo "The extension of the file provided is not correct."
    echo "Must be a '.pcapng' file; the PCAP Next Generation file format, that is a standard format for storing captured data over the network."
    echo "Exiting ..."
    exit -1 
fi

get_bytes()
{
    bytes_arraw=$1
    bytes=0
    for x in ${bytes_array[*]}; do
	    bytes=$[ $bytes + $x ];
    done
    echo $bytes
}


bytes_array=$(tshark -Y "ip.src ==11.0.0.1" -r $file -T fields -e frame.len)
bytes=$(get_bytes $bytes_array)
total_bytes=$bytes

bytes_array=$(tshark -Y "ip.src ==12.0.0.1" -r $file -T fields -e frame.len)
bytes=$(get_bytes $bytes_array)
total_bytes=$[$bytes + $total_bytes]

echo ""
echo "Total bytes transfered: $total_bytes Bytes"
bandwith_occupation1=$(bc <<< "($bytes1*100.0)/$total_bytes")
echo ""
echo "TAP 0: $bytes1 Bytes"
echo "Bandwidth occupation TAP 0: $bandwith_occupation1%"
echo ""
bandwith_occupation=$(bc <<< "($bytes*100.0)/$total_bytes")
echo "TAP 1: $bytes Bytes"
echo "Bandwidth occupation TAP 1: $bandwith_occupation%"
echo ""

