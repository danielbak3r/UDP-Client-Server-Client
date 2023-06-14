import socket
import threading
import queue
import random
import string
import time

localIP = "127.0.0.1"
localPort = 20002
bufferSize = 1024

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

messages = queue.Queue()
clients = []
clientsMethods = []

MultipleMessageVolume = 9

# Input settings by the user
# ClientIP1 = input("Enter Client 1 IP: ")
# ClientPort1 = input("Enter Client 1 port: ")
# ClientPort1 = int(ClientPort1)
# ClientIP2 = input("Enter Client 2 IP: ")
# ClientPort2 = input("Enter Client 2 port: ")
# ClientPort2 = int(ClientPort2)
# disruptor_frequency = input("Enter frequency of the disruption (0, 1): ")

# print("0) No method of transmission control")
# print("1) Multiple message transmission control method")
# method = input("Choose method of Transmission Control Protocol: ")

ClientIP1 = "127.0.0.1"
ClientPort1 = 9997
ClientIP2 = "127.0.0.1"
ClientPort2 = 9998
disruptor_frequency = 0.1

print("UDP server up and listening")

def delay(message):
    time.sleep(0.001*len(message))

def delpackets(message):
    time.sleep(0.001*len(message))

def multiple_message_method(prefix, message, client):
    for x in range(5):
        UDPServerSocket.sendto(prefix + message, client)

def CutMessages(message):
    n = 3
    CutMessage = [message[i:i + n] for i in range(0, len(message), n)]
    return CutMessage

def CheckSum(messages):
    ChckSumList = []
    for message in messages:
        asciisum = 0
        for letter in message:
            asciisum+=(ord(letter)-96)
        ChckSumList.append(asciisum)
    return  ChckSumList

# disruptor function
def disruptor(message, disruptor_frequency):
    glitched_mess = ""
    disruptor_frequency = float(disruptor_frequency)
    characters = string.ascii_letters + string.digits + string.punctuation
    message = str(message)
    print(message)
    for letter in message:
        random_numb = random.uniform(0, 1)
        if disruptor_frequency >= random_numb:
            letter = random.choice(characters)
            glitched_mess += letter
        else:
            glitched_mess += letter

    return glitched_mess


# Listen for incoming datagrams
def receive():
    while True:
        try:
            message, addr = UDPServerSocket.recvfrom(bufferSize)
            # Split message and method
            message = message.decode()
            message = str(message)
            x = message.split('!/')
            method = x[1]
            method = str(method[0])
            message = x[0]

            # client one or client two receive only
            if (addr[0] == ClientIP1 and addr[1] == ClientPort1) or (addr[0] == ClientIP2 and addr[1] == ClientPort2):
                #Delete packets greater than 1500 bytes
                if len(message)<1500:
                    messages.put((message, addr, method))
            else:
                pass
        except:
            pass

# Broadcast received datagrams
def broadcast():
    while True:
        while not messages.empty():
            message, addr, method = messages.get()
            print(addr)
            prefix = "Client " + addr[0] + ": "

            # print message
            message = message.encode()
            message = message.decode()
            message = str(message)
            print(message)
            print(prefix + message)

            prefix = str(prefix).encode()


            if addr not in clients:
                clients.append(addr)
                print(clients)

            portMethod = (addr[1], method)
            if portMethod not in clientsMethods:
                clientsMethods.append(portMethod)
                print(clientsMethods)
            for client in clients:
                x = 0
                while client[1] != clientsMethods[x][0]:
                    x += 1
                else:
                    # No transmission control method
                    if clientsMethods[x][1] == "0":
                        message = disruptor(message, disruptor_frequency)

                        # Delay of x ms per bytes
                        delay(message)

                        message = message.encode()
                        UDPServerSocket.sendto(prefix + message, client)

                    # Multiple transmission control message method
                    elif clientsMethods[x][1] == "1":

                        for x in range(MultipleMessageVolume):
                            # Delay of x ms per bytes
                            delay(message)

                            message_cp = disruptor(message, disruptor_frequency)
                            message_cp = message_cp.encode()
                            UDPServerSocket.sendto(prefix + message_cp, client)

                    # Split message control method
                    elif clientsMethods[x][1] == "2":
                         CutMessage_cp = []
                         ChkSumList_cp = []

                         CutMessage = CutMessages(message)
                         ChckSumList = CheckSum(CutMessage)

                         print(ChckSumList)
                         print(CutMessage)
                         content = 0
                         while content < len(CutMessage):
                             print(type(CutMessage[content]))
                             tmp = disruptor(CutMessage[content], disruptor_frequency)
                             CutMessage_cp.append(tmp)

                             tmp = disruptor(ChckSumList[content], disruptor_frequency)
                             print(tmp)
                             ChkSumList_cp.append(tmp)
                             content += 1

                         print(ChkSumList_cp)
                         print(CutMessage_cp)
                         UDPServerSocket.sendto(prefix + content, client)
                    else:
                        print("Wrong method for client: " + addr[0])
# Broadcast and Receive at the same time
t1 = threading.Thread(target = receive)
t2 = threading.Thread(target = broadcast)

t1.start()
t2.start()
