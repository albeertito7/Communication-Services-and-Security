#!/bin/bash

display_usage()
{
    echo -e "\nUsage: $0 [options] <infile>"
    echo -e "\nShell script that computes from the capture frame infile the percentatge of bandwidth ocuppation for each of the streams coming from C1-tap0 and C2-tap1."
    echo -e "\nrequired arguments:"
    echo "   infile:         Must be a .pcap or .pcapng file"
    echo -e "\noptional arguments:"
    echo "   -h, --help      Shows usage message to provide help"
} 

file=$1

if [ $# -eq 0 ]
then
    echo "error: No infile argument supplied."
    display_usage
    exit 1
elif [[ ( $* == "--help") ||  $* == "-h" ]] 
then 
    display_usage
    exit 0
elif [[ "${file##*.}" != "pcapng" && "${file##*.}" != "pcap" ]]
then
    echo "error: The extension of the file provided is not correct."
    display_usage
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

bandwith_occupation1=$(bc <<< "($tap0_bytes*100.0)/$total_bytes")
echo -e "\nTAP 0: $bytes1 Bytes"
echo "Bandwidth occupation TAP 0: $bandwith_occupation1%"

bandwith_occupation=$(bc <<< "($tap1_bytes*100.0)/$total_bytes")
echo -e "\nTAP 1: $bytes Bytes"
echo "Bandwidth occupation TAP 1: $bandwith_occupation%"

echo -e "\nTotal bytes: $total_bytes Bytes\n"

