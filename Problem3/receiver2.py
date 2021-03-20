import socket
from time import sleep
import threading
import time
import os

def SendAckSequence(ne):
    sleep(t_toack)
    s.sendto(('ACK-' + str(ne) + '-' + str(advertisedWindow)).encode('utf-8'),(HOST,PORTACK)) # enviar advertisedwindow
    print('----------------------------')
    print("SENT ACK ",ne,", AdvertiseWindow: ", advertisedWindow," - 3 or more segments in sequence",time.time()-start_time-1)
    print('----------------------------')

def SendAck_2sec(ne):
    s.sendto(('ACK-' + str(ne) + '-' + str(advertisedWindow)).encode('utf-8'),(HOST,PORTACK))
    print('----------------------------')
    print("SENT ACK ",ne,", AdvertiseWindow: ", advertisedWindow," - Without a correct reception (2s)",time.time()-start_time-1)
    print('----------------------------')

def thread_timer(): # temporitzador per revisar els ack's
    global timer
    while 1:
        if time.time() - timer>t_idle:
            SendAck_2sec(lastCorrectSegment+1)
            timer=time.time() # en cert moment ha de para denviar


HOST = 'localhost'        # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
PORTACK=50008

t_toack = 0.1
t_idle = 2.0 # Temps de recepcio
packetReceived = False

#global timer
#timer=time.time() # Timer inicialitzat (sino utilizar +100)

global lastCorrectSegment
lastCorrectSegment = -1

# Contador 3 o mes segments en sequencia:
sequence=0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,PORT))
NextExpected=0

global timer
start_time = timer = time.time()

p = threading.Thread(target=thread_timer) #timerControl
p.start()

advertisedWindow = 10

while 1:
    data, addr = s.recvfrom(1024)
    data = map(int,data.decode('utf-8').split("-"))
    error, num = data[0], data[1]

    if error==0:
        print('----------------------------')
        print("num:",num)
        print("NextExpected:", NextExpected)
        print('----------------------------')
        if  num==NextExpected:
            sequence+=1 # Actualitzem sequencia
            if (sequence>=3):
                SendAckSequence(num+1)
            timer=time.time() #Actualitzem temps
            lastCorrectSegment=num
            print("Correct segment",num)
            NextExpected+=1
        else:
            sequence=0
    else:
        sequence=0
