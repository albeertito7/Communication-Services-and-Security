import sys
import socket
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
from logger import Logger

HOST = 'localhost'
PORT = 50007
PORTACK = 50008
EXE_TIME=200

sys.stdout = Logger("logTransmitter")
start_time = time.time()
t_time = 1.0 # transmission time

Buffer = []
retrans_buffer = []
segment_register=[]
segment_retrans_register = []

MSS = 1
cwini = MSS
cwnd = cwini
effective_window = cwnd

cwmax = 4 # CWMAX = 4
rtt = 10
alpha = 0.8
srtt = rtt # assgined same value as rtt
last_sent = -1
last_ack = -1
t_out = 10 # init timeOut 10 s

# Plot
t_plot = []
srtt_plot = []
cwnd_plot = []
to_plot = []

def plot_thread():
    global t_plot, srtt_plot, cwnd_plot, to_plot, start_time
    while 1:
        t_plot.append(time.time() - start_time)
        srtt_plot.append(srtt)
        cwnd_plot.append(cwnd)
        #to_plot.append(t_out)
        time.sleep(1)

def make_plot(time, sRTT, cwnd, to):
    plt.plot(time, cwnd, label = "CWND") 
    plt.plot(time, sRTT, label = "sRTT")
    #plt.plot(time, to, label = "TimeOut")
    plt.xlabel('Time (s)') 
    plt.title('CWND and sRTT as a function of time') 
    plt.legend() 
    plt.savefig("plot.png")
    plt.show()
  
def process_ack():
    global last_ack, cwmax, cwnd, rtt, srtt, effective_window, t_out

    while 1:
        data,addr = s2.recvfrom(1024) # receiving data
        data = data.decode('utf-8').split('-')[1:]
        num = int(data[0]) - 1 # num segment

        # Karn/Patridge
        if num > last_ack:
            last_ack = num
            if num not in segment_retrans_register: # if not retransmitted segment
                print("ACK Num: " + str(num+1) + " recvd | Retransmission: False => UPDATE sRTT")
                for key in segment_register: 
                    if key['segment'] == num:
                        rtt = (time.time() - start_time)-key['timeSent']
                        srtt = alpha*srtt + (1 - alpha)*rtt # update srtt Karn/Patridge
                        t_out = 2*srtt # update timeOut
            else:
                print("ACK Num: " + str(num+1) + " recvd | Retransmission: True => NOT update sRTT")

            # SlowStart => when ACK received
            if cwnd < cwmax:
                cwnd += MSS
            else:
                cwnd += MSS/cwnd
                cwmax = min(cwmax, cwnd)

            # update effective window
            effective_window =  int(cwnd - (last_sent - last_ack)) # int(min(cwnd, advertisedWindow) - (LastSent-LastAck))

        print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Ack received | Num:",num+1,"| EffWin:",("%.2f" % effective_window), "| CWND:",("%.2f" % cwnd), "| RTT:",("%.2f" % rtt),"| sRTT:", ("%.2f" % srtt),"| TOut:",("%.2f" % t_out),"| LastACK:",last_ack,"| LastSent:",last_sent)


def send_retrans_buffer():
    while len(retrans_buffer) > 0:
            num = retrans_buffer[0]
            del retrans_buffer[0]

            datagram = '0-' + str(num) # datagram no error when retransmission

            segment_retrans_register.append(num) # segments retransmitted register
            segment_register.append({
                'segment': num,
                'timeSent': time.time() - start_time
            }) # segments register
            
            time.sleep(t_time) # transmission time
            s.sendto(datagram.encode('utf-8'),(HOST,PORT))

            print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Segment retransmission | Num:",num,"| EffWin:",("%.2f" % effective_window), "| CWND:",("%.2f" % cwnd), "| RTT:",("%.2f" % rtt),"| sRTT:", ("%.2f" % srtt),"| TOut:",("%.2f" % t_out),"| LastACK:",last_ack,"| LastSent:",last_sent) 


def time_out(num):
    global retrans_buffer, cwnd, cwmax, effective_window

    time.sleep(t_out) # waiting
    if num > last_ack: # if ack not received => retransmission

        print("Time:",("%.2f" % (time.time() - start_time)),"| Event: Segment timeOut | Num:",num,"| RetransBuffer:",retrans_buffer,"+ [",num,"] | EffWin:",("%.2f" % effective_window), "| CWND:",("%.2f" % cwnd),"| RTT:",("%.2f" % rtt),"| sRTT:", ("%.2f" % srtt),"| TOut:",("%.2f" % t_out),"| LastACK:",last_ack,"| LastSent:",last_sent)

        retrans_buffer.append(num)
        send_retrans_buffer()

        # Slow-start => When TimeOut
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))
        effective_window = int(cwnd - (last_sent - last_ack))

def send_buffer():
    global Buffer, last_sent, effective_window, segment_register

    if len(Buffer) > 0 and effective_window > 0 and time.time() - start_time < EXE_TIME: # if data to send and effective window is okey
            num = Buffer.pop(0)

            if is_prime(num): # prime number segments initially lost => retransmission
                event = "Sent segment lost" # Event:TCP lost
                error = '1'
            else:
                event = "Sent segment" # Event:TCP sent
                error = '0'

            '''--------- Operacions ---------'''
            #Diccionari {segment;temps}
            last_sent = num
            effective_window = int(cwnd - (last_sent - last_ack)) # calc effective window based on congestion network and transmitter thresholds

            datagram = error + '-' + str(num) # datagram build
            segment_register.append({
                'segment': num, 
                'timeSent': time.time() - start_time
            }) # register of segments sent at what time

            time.sleep(t_time)
            print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| Num:",num,"| EffWin:",("%.2f" % effective_window), "| CWND:",("%.2f" % cwnd), "| RTT:",("%.2f" % rtt),"| sRTT:", ("%.2f" % srtt),"| TOut:",("%.2f" % t_out),"| LastACK:",last_ack,"| LastSent:",last_sent)
            s.sendto(datagram.encode('utf-8'), (HOST,PORT))

            threading.Thread(target=time_out, args=(num,)).start() # TimeOut thread for each segment

def is_prime(n): # Prime numbers check
    if n == 2 or n == 3: return True
    if n%2 == 0 or n < 2: return False
    for i in range(3,int(n**0.5)+1,2): # only odd numbers
        if n%i == 0:
            return False
    return True

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s2.bind((HOST,PORTACK))

threading.Thread(target=process_ack).start() # thread to receive the ACK's
threading.Thread(target=plot_thread).start() # thread to collect data and make the corresponding plots

for i in range(400): Buffer.append(i) # init buffer
start_time = time.time()

while time.time()-start_time < EXE_TIME: # time control
    send_buffer()

make_plot(t_plot, srtt_plot, cwnd_plot, to_plot)
