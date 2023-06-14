import socket
import threading
from collections import Counter
import time

# Input settings by user
# ServerIP = input("Enter server IP: ")
# ServerPort = input("Enter server port: ")
# ServerPort = int(ServerPort)
# ClientPort = input("Enter your port: ")
# ClientPort = int(ClientPort)

print("0) No method of transmission control")
print("1) Multiple message transmission control method")
print("2) Split message control method")
method = input("Choose method of Transmission Control Protocol: ")
test = input("Test? (y/n): ")
ServerIP = "127.0.0.1"
ServerPort = 20002
ClientPort = 9997

serverAddressPort = (ServerIP, ServerPort)
bufferSize = 1024

# Tester variables
TestSampleSize = 50000
global MessagesVolume
MessagesVolume = 0
TestCorrectMessages = 0
TestIncorrectMessages = 0

MultipleMessageVolume = 9

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPClientSocket.bind(("127.0.0.1", ClientPort))

prefix = "connected!/" + method
UDPClientSocket.sendto(prefix.encode(), serverAddressPort)

messages = []
messageCounter = 0

def multiple_message_method_probability(messages):
    print(messages)
    length = len(messages[1])
    messagesComparison_Sorted = []
    prob_message = []

    # Sort letters in message
    x = 0
    while x < length:
        messagesComparison_W = []
        for message in messages:
            messagesComparison_W.append(message[x])
        # print(messagesComparison_W)
        messagesComparison_Sorted.append(messagesComparison_W)
        x += 1

    # print(messagesComparison_Sorted)
    # Take letters with higher probability
    for message in messagesComparison_Sorted:
        counter = Counter(message)
        most_frequent = counter.most_common(1)[0]
        most_frequent = most_frequent[0]
        prob_message.append(most_frequent)

    # merge letters into string
    message = ''.join(prob_message)
    messages.clear()
    return message


def testerType(sampleSize):
    testStr = ("1234567890!/" + method).encode()
    testStrsize = 10
    loopSize = sampleSize/testStrsize
    loopSize = int(loopSize)
    x = 0
    while x < loopSize:
        time.sleep(0.001)
        UDPClientSocket.sendto(testStr, serverAddressPort)
        x += 1
    return loopSize

def testerCount(message):
    global TestIncorrectMessages, TestCorrectMessages
    testStr = "1234567890"
    message = message[-10:]
    if message == testStr:
        TestCorrectMessages += 1
    else:
        if message == " connected":
            TestCorrectMessages += 1
        else:
            TestIncorrectMessages += 1




def receive():
    messageCounter = 0
    TotalMessageReceive = 0
    global TestCorrectMessages, TestIncorrectMessages
    while True:
        try:
            match method:
                # No transmission control method
                case "0":
                    message, _ = UDPClientSocket.recvfrom(bufferSize)
                    match test:
                        case "n":
                            print(message.decode())
                        case "y":
                            print(message.decode())
                            testerCount(message.decode())
                            if ((TestCorrectMessages + TestIncorrectMessages) == MessagesVolume+1):
                                print("Correct: " + str(TestCorrectMessages))
                                print("Incorrect: " + str(TestIncorrectMessages))
                                print("Message Volume: " + str(MessagesVolume+1))
                                print(TestCorrectMessages/(MessagesVolume + 1))
                # Multiple transmission control message method
                case "1":
                    match test:
                        case "n":
                            message, _ = UDPClientSocket.recvfrom(bufferSize)
                            messages.append(message.decode())
                            messageCounter += 1
                            if(messageCounter == MultipleMessageVolume):
                                messageCounter = 0
                                message = multiple_message_method_probability(messages)
                                print(message)
                        case "y":
                            message, _ = UDPClientSocket.recvfrom(bufferSize)
                            messages.append(message.decode())
                            messageCounter += 1
                            TotalMessageReceive += 1
                            print(messages)
                            if (messageCounter == MultipleMessageVolume):
                                messageCounter = 0
                                message = multiple_message_method_probability(messages)
                                print(message)
                                testerCount(message)
                                if ((TestCorrectMessages + TestIncorrectMessages) == MessagesVolume+1):
                                    print("Correct: " + str(TestCorrectMessages))
                                    print("Incorrect: " + str(TestIncorrectMessages))
                                    print("Message Volume: " + str((MessagesVolume + 1)))
                                    print("Total Message Volume: " + str((MessagesVolume + 1)*MultipleMessageVolume))
                                    print(TestCorrectMessages / ((MessagesVolume + 1)))
               # Split message control method
                case "2":
                    message, _ = UDPClientSocket.recvfrom(bufferSize)
                    match test:
                        case "n":
                            print(message.decode())
                        case "y":
                            print(message.decode())

        except:
            pass


t1 = threading.Thread(target=receive)
t1.start()

while True:
    message = input("")
    if message == "$quit":
        exit()
    else:
        match test:
            case "n":
                message = message + "!/" + method
                UDPClientSocket.sendto(message.encode(), serverAddressPort)
            case "y":
                # Tester and size of a sample in bytes
                MessagesVolume += testerType(TestSampleSize)



