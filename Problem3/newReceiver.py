import socket
from time import sleep
import threading
import time
import os

def SendAck(ne):
    #time.sleep(t_toack)  # al no tenir mida s'envia al moment
    datagram = 'ACK-' + str(ne)
    s.sendto(datagram.encode('utf-8'), (HOST, PORTACK))
    print("SENT ACK ", ne)

def SendAck_2sec(ne):
    s.sendto(('ACK-' + str(ne) + '-' + str(advertisedWindow)).encode('utf-8'),(HOST,PORTACK))
    print('----------------------------')
    print("SENT ACK ",ne,", AdvertiseWindow: ", advertisedWindow," - Without a correct reception (2s)",time.time()-start_time-1)
    print('----------------------------')

def SendAckSequence(ne):
    #sleep(t_toack)
    s.sendto(('ACK-' + str(ne) + '-' + str(advertisedWindow)).encode('utf-8'), (HOST,PORTACK)) # enviar advertisedwindow
    print('----------------------------')
    print("SENT ACK ",ne,", AdvertiseWindow: ", advertisedWindow," - 3 or more segments in sequence",time.time()-start_time-1)
    print('----------------------------')

def thread_timer():
    global timer
    while 1:
        if time.time() - timer > t_idle: # si han passat més de dos segons respecte el temps actual i el ultim packet rebut correctament en sequencia
            SendAck_2sec(NextExpected)
            timer = time.time()


HOST = 'localhost'        # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
PORTACK=50008

t_toack = 0.1
t_idle = 2.0 # Temps de recepcio
packetReceived = False

#global timer
#timer=time.time()+100 # Timer inicialitzat (sino utilizar +100)

global lastCorrectSegment
lastCorrectSegment = -1

# Contador 3 o mes segments en sequencia:
sequence=0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,PORT))
NextExpected=0

global timer # time last segment correctly received
timer = time.time()
start_time = time.time()

advertisedWindow = 10
bufferMaxSize = 10 # advertisedWindow = bufferMaxSize - len(Buffer)
Buffer = []

first = False

while 1:
    data, addr = s.recvfrom(1024)

    if not first:
        timer = time.time()
        p = threading.Thread(target=thread_timer) #timerControl
        p.start()
        first = True

    data = data.decode('utf-8')
    error = int(data.split("-")[0])
    num = int(data.split("-")[1])

    print("Received Num: " + str(num) + " | Error: " + str(error))
    # si no hi ha error, i el packet no lhe rebut => afegim al buffer de recepció
    if error == 0 and num >= NextExpected and num not in Buffer:
        Buffer.append(num)
        Buffer.sort()
        print("Buffer:" + str(Buffer))
        if num == NextExpected: # correctly received
            sequence = 0
            for x in range(len(Buffer)-1):
                if Buffer[x]+1 == Buffer[x+1]:
                    sequence += 1
                else:
                    break
                
            NextExpected = Buffer[sequence]+1
            print("Sequence: " + str(sequence) + " | NextExpected: " + str(NextExpected))
            if sequence >= 2:
                SendAckSequence(NextExpected)
                print("Buffer read: " + str(Buffer) + " => " + str(Buffer[sequence+1:]))
                Buffer = Buffer[sequence+1:]
            timer = time.time() # actualitzem time correct reception (what was expected)
