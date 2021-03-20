import matplotlib
import matplotlib.pyplot as plt 
import socket
import time
import random
import threading
import sys

HOST = 'localhost'
PORT = 50007
PORTACK = 50008

LastSent = -1
LastAck = -1
TO = 10. #timeout 10 sec
LimitTime=200
start_time = time.time()

Buffer=[]
RetransBuffer=[]
segmentList=[]
segmentRetrans=[]

#File parameters
resultFile = 'result.txt'

# Plot parameters
tPlot = []
srttPlot = []
cwndPlot = []
toPlot = []

#Parametres 
MSS=1
cwini = MSS
cwnd = cwini
effectiveWindow = cwnd
advertisedWindow = sys.maxsize
cwMaxSize = 4
cwmax= 4
event = " "
rtt = 10#TO/2
alpha = 0.8
srtt = rtt #Assignem el mateix valor que rtt
#srtt = alpha*srtt+(1-alpha)*rtt #Karn/Patridge RTT
isOut = False 
first = True

progressTime = time.time() #variable per a comprovar temps denviament

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
t_time = 1.0 # transmission time
s2.bind((HOST,PORTACK))

def plotFunction():
    global tPlot,srttPlot,cwndPlot,toPlot,start_time
    while 1:
        tPlot.append(time.time()-start_time)
        srttPlot.append(srtt)
        cwndPlot.append(cwnd)
        toPlot.append(TO)
        time.sleep(1)

# CWND i RTT en funcio del temps 
def ploting(time, sRTT, cwnd, to):
    plt.plot(time, cwnd, label = "CWND") 
    plt.plot(time, sRTT, label = "SRTT")
    plt.plot(time, to, label = "TimeOut")
    plt.xlabel('Time(s)') 
    plt.title('cwnd and sRTT as a function of time') 
    plt.legend() 
    plt.savefig("result.png")
    plt.show()
  
def ProcessAck():
    global Buffer, LastAck, cwmax, cwnd, rtt, srtt, effectiveWindow, segmentList, TO, advertisedWindow

    while 1:
        data,addr = s2.recvfrom(1024)
        data = data.decode('utf-8')
        num = int(data.split('-')[1])-1
        advertisedWindow = int(data.split('-')[2])

        #if num==(LastAck+1):
        '''--------- SlowStart ACK Received ---------'''
        #Karn/Patridge Actualitzem rtt quan ACK respecte el temps del ultim segment enviat del corresponent ack

        if num > LastAck:
            LastAck = num
            if num not in segmentRetrans: # si no s'ha retransmés
                print('----------------------------')
                print("ACK Num: " + str(num+1) + " recvd | Retransmission: False => UPDATE sRTT")
                print('----------------------------')
                for key in segmentList: 
                    if key['segment'] == num:
                        rtt = (time.time()-start_time)-key['timeSent']
                        srtt = alpha*srtt+(1-alpha)*rtt #Update srtt Karn/Patridge
                        TO = 2*srtt # + (time.time()-start_time)
            else:
                print('----------------------------')
                print("ACK Num: " + str(num+1) + " recvd | Retransmission: True => NOT update sRTT")
                print('----------------------------')

            # Formules SlowStart => When ACK received
            if cwnd < cwmax:
                cwnd += MSS
            else:
                cwnd += MSS/cwnd
                cwmax = min(cwmax, cwnd)
            
            #Trace("ACK rec"+data)

            #Update effective Window = cwnd - non rcv ACK
            effectiveWindow =  int(cwnd - (LastSent - LastAck)) # int(min(cwnd, advertisedWindow) - (LastSent-LastAck))
            
        #Prints de recepcio
        event = 'ACK packet ' + str(num+1) +' recvd' # Event:ack rebut
        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO),"| LastSent:",("%.2f" % LastSent),"| LastACK:",("%.2f" % LastAck))


def SendRetransBuffer():
    global TO
    while len(RetransBuffer) > 0:
        #if effectiveWindow > 0:
            num=RetransBuffer[0]
            del RetransBuffer[0]
            datagram='0-' + str(num)

            segmentRetrans.append(num) # segments retransmessos
            #TO = 2*srtt
            time.sleep(t_time) # Segment Transmission Time
            s.sendto(datagram.encode('utf-8'),(HOST,PORT))
            #Trace('sent retrans: '+datagram)

            #Diccionari {segment;temps}
            progressTime = time.time()
            segmentList.append({'segment': num,'timeSent': progressTime-start_time})

            print('----------------------------')
            '''--------- SlowStart SendRetransBuffer ---------'''
            event = 'Retransmission Num: ' + str(num) + ' sgmnt' # Event:ack rebut
            print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO)) 
            print('----------------------------')


def TimeOut(num):
    global RetransBuffer, LastAck, cwnd, cwmax, isOut, TO, effectiveWindow, LastSent
    print('----------------------------')
    print("Waiting ACK Num: " + str(num) + " | TO: " + str(TO))
    print('----------------------------')

    time.sleep(TO) # espera el timeout
    if num > LastAck: # no s'haurà rebut el ack => retransmissio
        '''--------- SlowStart TimeOut ---------'''
        event = 'TimeOUT: ' + str(num) + ' segment' # Event:TimeOut

        print('----------------------------')
        print("TimeOut Num:" + str(num) + " | TO: " + str(TO) + " | RetransBuffer: " + str(RetransBuffer) + " + [" + str(num) + "]")
        print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO),"| num:",("%.2f" % num),"| LastACK:",("%.2f" % LastAck))
        print('----------------------------')

        RetransBuffer.append(num)
        SendRetransBuffer()

        # Slow-start => When TimeOut
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))
        effectiveWindow = int(cwnd - (LastSent - LastAck)) # int(min(cwnd, advertisedWindow) - (LastSent-LastAck))

        #TO = 2*srtt #+ (time.time()-start_time)


def SendBuffer():
    global Buffer, LastSent, effectiveWindow, rtt, srtt, segmentList, event, progressTime, isOut, first ,TO, advertisedWindow

    if len(Buffer) > 0 and effectiveWindow > 0 and time.time()-start_time < LimitTime: # hi ha data per enviar, i podem enviar
            num = Buffer.pop(0)

            if isPrime(num): # Segments nombres Primers es perden
                event = 'TCP segment '+ str(num) + ' lost' # Event:TCP perdut
                error = '1'
            else:
                event = 'TCP segment '+ str(num) + ' sent' # Event:TCP enviat
                error = '0'

            '''--------- Operacions ---------'''
            #Diccionari {segment;temps}
            LastSent = num
            effectiveWindow = int(cwnd - (LastSent - LastAck)) # int(min(cwnd, advertisedWindow) - (LastSent-LastAck))
            
            datagram = error +'-'+ str(num)   #   Segment:  errorindicator-seqnum

            progressTime = time.time()
            segmentList.append({'segment': num, 'timeSent': progressTime-start_time})

            time.sleep(t_time) # temps transmissio

            print('----------------------------')
            print("Time:",("%.2f" % (time.time() - start_time)),"| Event:", event,"| EffWin:",effectiveWindow, "| CWND:",cwnd, "| rtt:",("%.2f" % rtt),"| srtt:", ("%.2f" % srtt),"| TimeOut:",("%.2f" % TO))
            print('----------------------------')
            s.sendto(datagram.encode('utf-8'), (HOST,PORT))

            t = threading.Thread(target = TimeOut, args=(num,))
            t.start()

            
def Trace(mess):
    t=time.time()-start_time
    print(t,'|',"'"+mess+"'")

def isPrime(n): # Prime numbers
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3,int(n**0.5)+1,2): # only odd numbers
        if n%i==0:
            return False
    return True


x = threading.Thread(target=ProcessAck) # thread per escoltar els acks que es rebin
x.start()

y = threading.Thread(target=plotFunction) # thread per collectar dades i fer els grafics
y.start()

for i in range(400): Buffer.append(i) # ompleno buffer

start_time = time.time()

while time.time()-start_time < LimitTime: # mentres el temps
    SendBuffer()

ploting(tPlot,srttPlot,cwndPlot, toPlot) # al finalitzar el temps, es crear el grafic/plot
