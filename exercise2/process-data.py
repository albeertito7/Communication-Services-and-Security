import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# sim-trace.tr
header = ['Event_Type', 'Time', 'Link_Source_Node', 'Link_Destination_Node', 'Segment_Type', 'Segment_Size', 'Flags', 'Flow_Identifier', 'Segment_Source_Address', 'Segment_Destination_Address', 'Segment_Number', 'Segment_Identifier']
df = pd.read_csv('sim-trace.tr', sep=' ', names = header)
df.head()

df.info()

# Lost Packets
lost_packages = df.Event_Type == 'd'
ids = df[lost_packages].Segment_Source_Address

n0_lost = ids == 0 #TCP Vegas
n1_lost = ids == 1 #TCP Reno
n2_lost = ids == 2 #TCP Tahoe

print("Lost Packages")
print("Node 0:\t", sum(n0_lost))
print("Node 1:\t", sum(n1_lost))
print("Node 2:\t", sum(n2_lost))
print("Total:\t", ids.count())


# Transferred bytes
def getNode(row, node):
  return row.Link_Source_Node == int(node) and row.Event_Type == '-'

n0_packets = df.apply(getNode, axis = 1, args=('0'))
n1_packets = df.apply(getNode, axis = 1, args=('1'))
n2_packets = df.apply(getNode, axis = 1, args=('2'))
n3_packets = df.apply(getNode, axis = 1, args=('3'))
n4_packets = df.apply(getNode, axis = 1, args=('4'))

n0_bytes = sum(df[n0_packets].Segment_Size)
n1_bytes = sum(df[n1_packets].Segment_Size)
n2_bytes = sum(df[n2_packets].Segment_Size)
n3_bytes = sum(df[n3_packets].Segment_Size)
n4_bytes = sum(df[n4_packets].Segment_Size)
total_bytes = n0_bytes + n1_bytes + n2_bytes + n3_bytes + n4_bytes

print("Transferred bytes:")
print("Node 0:\t", n0_bytes)
print("Node 1:\t", n1_bytes)
print("Node 2:\t", n2_bytes)
print("Node 3:\t", n3_bytes)
print("Node 4:\t", n4_bytes)
print("Total:\t", total_bytes)


# sim-trace.rtt
header2 = ['Node', 'Time', 'rtt', 'srtt', 'cwnd', 'cwmax', 'bo']
df2 = pd.read_csv('sim-trace.rtt', sep=' ', names = header2)
df2.head()

time = df2[df2.Node==0].Time
cwnd0 = df2[df2.Node==0].cwnd
cwnd1 = df2[df2.Node==1].cwnd
cwnd2 = df2[df2.Node==2].cwnd

plt.plot(time,cwnd2, label='TCP Vegas', color='red')
plt.plot(time,cwnd1, label='TCP Reno', color='green')
plt.plot(time,cwnd0, label='TCP Tahoe', color='blue')

plt.title('Congestion Windows x Time')
plt.xlabel('Time (s)')
plt.ylabel('Congestion Window (MSS)')
plt.legend(loc='upper right')
plt.show()