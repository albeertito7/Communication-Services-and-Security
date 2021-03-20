import matplotlib
import matplotlib.pyplot as plt
import socket
import time
import random
import threading

HOST = 'localhost'
PORT = 50007
PORTACK = 50008

LastSent = -1
LastAck = -1
TO = 10
LimitTime = 200
start_time = time.time()

Buffer = []
RetransBuffer = []
segmentList=[]

# Output file
resultFile = 'result.txt'

# Plotting vars
tPlot = []
srttPlot = []
cwndPlot = []

# Parameters
MSS = 1
cwini = MSS
cwnd = cwini
effectiveWindow = cwnd
advertisedWindow = 0
cwmax = 4
event = " "
rtt = TO/2
alpha = 0.8
srtt = rtt
srtt = alpha*srtt+(1-alpha)*rtt
isOut = False # packet perdut
first = True

progressTime = time.time()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
t_time=1.0
s2.bind((HOST, PORTACK))

def plotFunction():
    global tPLot, srttPlot, cwndPlot, start_time
    while True:
        tPlot.append(time.time() - start_time)
        srttPlot.append(srtt)
        cwndPlot.append(cwnd)
        time.sleep(1) #at each second, collect data

def ploting(time, srtt, cwnd):
    plt.plot(time, cwnd, lable = 'CWND')
    plt.plot(time, srtt, label = 'SRTT')
    plt.xlabel('Time(s)')
    plt.title('cwnd and srtt as a function of time')
    plt.legend()
    plt.savefig("result.png")
    plt.show()

def ProcessAck():
    global Buffer, LastAck, cwmax, cwnd, rtt, srtt, effectiveWindow, segmentList, TO
    while True:
        data, addr = s2.recvfrom(1024)
        data = data.decode('utf-8')
        num=int(data.split('-')[1])-1

        for key in segmentList:
            if key['segment']==num:
                rtt = (time.time()-start_time)-key['time']
    
        srtt = alpha*srtt + (1-alpha)*rtt

        if cwnd < cwmax:
            cwnd += MSS
        else:
            cwnd += MSS/cwnd
            cwmax = min(cwmax, cwnd)
        
        LastAck = num

        effectiveWindow = int(cwnd-(LastSent-LastAck))

        event = 'ACK packet '+str(num+1)+' recvd' # Event:ack rebut
        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO),"| LastSent:",("%.2f" % LastSent),"| LastACK:",("%.2f" % LastAck))

def SendRetransBuffer():
    global TO
    while len(RetransBuffer) > 0:
        num=RetransBuffer[0]
        datagram='0-'+str(num)
        del RetransBuffer[0]
        time.sleep(t_time)
        s.sendto(datagram.encode('utf-8'), (HOST, PORT))

        progressTime=time.time()
        segmentList.append({'segment':num,'time':progressTime-start_time})

        event = 'Sent rtrns: '+str(num)+' sgmnt' # Event:ack rebut
        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO))


def TimeOut(num):
    global RetransBuffer, LastAck, cwnd, cwmax, isOut, TO
    time.sleep(TO)
    if num>=LastAck+1:
        isOut = False
        event = 'TimeOut: ' + str(num) + ' segment'
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))

        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO),"| num:",("%.2f" % num),"| LastACK:",("%.2f" % LastAck))
        RetransBuffer.append(num)
        SendRetransBuffer() # retransmetre els paquets perduts

def SendBuffer():
    global Buffer, LastSent, effectiveWindow, rtt, srtt, segmentList, event, progressTime, isOut, first, TO

    if effectiveWindow > 0: # Able to send?
        num=Buffer[0]
        del Buffer[0]
        error = '0'

        if not isOut and not first: # si sha perdut un packet actualitzem el timeOut (el primer cop no ho comprovem al no haverse enviat cap packet)
            T0 = 2*srtt + (time.time() - start_time)
            print("TimeOut Update: ", TO)

        event = 'TCP segment '+str(num)+' sent' # Event:TCP enviat
        datagram=error+'-'+str(num)   # Segment:  errorindicator-seqnum
        time.sleep(t_time)
        LastSent=num

        first = False
        
        progressTime = time.time()
        segmentList.append({'segment': num, 'time': progressTime-start_time})

        effectiveWindow = int(cwnd - (LastSent-LastAck))

        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO))
        s.sendto(datagram.encode('utf-8'), (HOST, PORT))
        t = threading.Thread(target=TimeOut, args=(num,))
        t.start()

def main():
    global Buffer, start_time

    x = threading.Thread(target=ProcessAck) # thread to process received ACKs
    x.start()

    y = threading.Thread(target=plotFunction) # thread to collect plotting data at each unit time
    y.start()

    [Buffer.append(i) for i in range(50)]
    start_time = time.time()

    while len(Buffer) > 0 and time.time() - start_time < LimitTime: # execution during 200 seconds
        SendBuffer()
    
    ploting(tPlot, srttPlot, cwndPlot)

if __name__ == '__main__':
    main()