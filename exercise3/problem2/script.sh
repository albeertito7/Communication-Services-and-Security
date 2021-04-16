#!/bin/bash

display_usage()
{
    echo -e "\nUsage: $0 [.pcapng file] \n" 
} 

file=$1

if [ $# -eq 0 ]
then
    echo "No file argument supplied. Must be specified the .pcapng file to be evaluated."
elif elif [[ ( $# == "--help") ||  $# == "-h" ]] 
then 
    display_usage
    exit 0
elif [ "${file##*.}" != "pcapng" ]
then
	echo "The extension of the file provided is not correct."
    echo "Must be a '.pcapng' file; the PCAP Next Generation file format, that is a standard format for storing captured data over the network."
    echo "Exiting ..."
    exit -1 
fi

echo "Processing $file file ..."

get_bytes()
{
    bytes_arraw=$1
    bytes=0
    for x in ${bytes_array[*]}; do
	    bytes=$[ $bytes + $x ];
    done
    echo $bytes
}


bytes_array=$(tshark -Y "ip.src == 11.0.0.1" -r $file -T fields -e frame.len)
tap0_bytes=$(get_bytes $bytes_array)
total_bytes=$tap0_bytes

bytes_array=$(tshark -Y "ip.src == 12.0.0.1" -r $file -T fields -e frame.len)
tap1_bytes=$(get_bytes $bytes_array)
total_bytes=$[$tap1_bytes + $total_bytes]

echo ""
echo "Total bytes transfered: $total_bytes Bytes"
bandwith_occupation1=$(bc <<< "($tap0_bytes*100.0)/$total_bytes")
echo ""
echo "TAP 0: $bytes1 Bytes"
echo "Bandwidth occupation TAP 0: $bandwith_occupation1%"
echo ""
bandwith_occupation=$(bc <<< "($tap1_bytes*100.0)/$total_bytes")
echo "TAP 1: $bytes Bytes"
echo "Bandwidth occupation TAP 1: $bandwith_occupation%"
echo ""

