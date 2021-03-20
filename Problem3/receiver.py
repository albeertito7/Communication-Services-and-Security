import socket
import threading
import time
import os

def SendAckSequence(num): # send immediately
    s.sendto(('ACK-' + str(num)).encode('utf-8'), (HOST,PORTACK))
    print("SENT ACK ", num,"TIME", time.time()-start_time-1)

def SendAck_2sec(ne):
    s.sendto(('ACK-'+str(ne)).encode('utf-8'),(HOST,PORTACK))
    print('-' * os.get_terminal_size().columns)
    print("SENT ACK ",ne,"- Without a correct reception (2s)", time.time()-start_time-1)
    print('-' * os.get_terminal_size().columns)

def thread_timer(): # temporitzador per revisar els ack's
    global timer
    while True:
        if (time.time() - timer) > t_idle:
            SendAck_2sec(lastCorrectSegment+1)
            timer=time.time()#en cert moment ha de para denviar


HOST = 'localhost'
PORT = 50007
PORTACK = 50008

t_toack = 1.0
t_idle = 2.0

global timer
timer = time.time()+5

global lastCorrectSegment
lastCorrectSegment = -1

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

p = threading.Thread(target=thread_timer)
p.start()

sequence = 0
NextExpected = 0
start_time = time.time()

while True:
    data, addr = s.recvfrom(1024)
    data = data.decode('utf-8')
    error = int(data.split("-")[0])
    num = int(data.split("-")[1])

    if error == 0: # no error
        print('-' * os.get_terminal_size().columns)
        print("num:",num)
        print("NextExpected:", NextExpected)
        print('-' * os.get_terminal_size().columns)

        if num == NextExpected:
            sequence += 1
            if sequence >= 3:
                SendAckSequence(num+1)
            time=time.time()
            lastCorrectSegment=num
            print("Correct segment", num)
            NextExpected+=1
        else:
            sequence = 0
    else:
        sequence = 0
