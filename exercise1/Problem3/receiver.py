import sys
import os
import socket
import threading
import time
from logger import Logger

sys.stdout = Logger("logReceiver")

HOST = 'localhost' # Symbolic name meaning all available interfaces
PORT = 50007 # Arbitrary non-privileged port
PORTACK = 50008

global timer
start_time = timer = time.time()
t_time = 0.1 # transmission time
t_idle = 2.0
next_expected = 0
Buffer = []
first = False

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,PORT))

def send_ack_2sec(ne):
    time.sleep(t_time)
    s.sendto(('ACK-' + str(ne)).encode('utf-8'),(HOST,PORTACK))
    print("SEND ACK ",ne," - Without a correct reception (2s) | Time:",("%.2f" % (time.time() - start_time)))

def send_ack_sequence(ne):
    time.sleep(t_time)
    s.sendto(('ACK-' + str(ne)).encode('utf-8'), (HOST,PORTACK))
    print("SEND ACK ",ne," - 3 or more segments in sequence | Time:",("%.4f" % (time.time() - start_time)))

def thread_timer():
    global timer
    while 1:
        if time.time() - timer > t_idle: # si han passat més de dos segons respecte el temps actual i el ultim packet rebut correctament en sequencia
            send_ack_2sec(next_expected)
            timer = time.time()

# main thread
while 1:
    data, addr = s.recvfrom(1024)

    if not first:
        threading.Thread(target=thread_timer).start() # thread timer control not receving correctly segments
        first = True

    data = list(map(int,data.decode('utf-8').split("-")))
    error, num = data[0], data[1]

    print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Received Segment | Num:",num,"| Error:",error)

    if error == 0 and num >= next_expected and num not in Buffer: # if not error and new packet => add packet to the Buffer
        Buffer.append(num) # add
        Buffer.sort() # sort list

        print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Segment Added | Num:",num,"| Buffer:",Buffer)
        if num == next_expected: # segment correctly received
            sequence = 0
            # checkin if sequence of 3 or more
            for x in range(len(Buffer)-1):
                if Buffer[x]+1 == Buffer[x+1]:
                    sequence += 1
                else:
                    break
                
            next_expected = Buffer[sequence]+1
            if sequence >= 2: # if sequence
                print("Time:",("%.2f" % (time.time() - start_time)),"| Event: 3 or more segments in sequence | Buffer read: ",Buffer,"=>",Buffer[sequence+1:],"| Next Expected:",next_expected,"| Sequence:",sequence)
                send_ack_sequence(next_expected)
                Buffer = Buffer[sequence+1:] # slice buffer => application read
            else:
                print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Next Expected Update | Buffer: ",Buffer,"| Next Expected:",next_expected, "Sequence:",sequence)
            timer = time.time() # set time cuz correct reception done (the segment that what was expected)
