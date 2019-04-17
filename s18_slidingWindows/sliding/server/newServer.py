from socket import *
import sys, os, time 

'''
packetType
action
status 
packetNumber
TimeStamp
windowSize  
payloadSize
fileName
fileSize
****
payload
'''

class ErrorQueue():

    def __init__(self):
        self.head = None
    
    def enqueue(self, packet):
        if(self.head is None):
            self.head = Node(packet)
            return self.head
        temp = self.head
        while(temp.next != None):
            temp = temp.next
        temp.next = Node(packet)
        
        return self.head
    
    def dequeue(self):
        if(self.head is None):
            return None
        if(self.head.next is None):
            self.head = None 
            return self.head
        temp = self.head
        deletedPacket = self.head.packet
        self.head.packet = self.head.next.packet
        self.head.next = self.head.next.next
        temp = None
        return self.head, deletedPacket
    
    def printQueue(self, node):
        while node != None:
            print(node.packet)
            node = node.next
        print(" ")
    
    def checkPacket(self, packet):
        temp = self.head
        while temp != None:
            if(temp.packet == packet):
                return True
            temp = temp.next 
        return False


class Node():
    def __init__(self, packet):
        self.packet = packet
        self.next = None 
    
    def getNext(self):
        return self.next
    
    def getWord(self):
        return self.word
class slidingServer():

    def __init__(self, socket):
        self.socket = socket 
        self.clientAddr = ("localhost", 50000)
        self.packetTracker = []
        self.packetsReceived = []
        self.lastPacket = ""
        self.tries = 0
        self.fileSize = 0
        self.windowSize = 1
        self.packetNumber = 0
    
    def reset(self):
        self.packetTracker = []
        self.packetsReceived = []
        self.lastPacket = ""
        self.tries = 0
        self.fileSize = 0
        self.windowSize = 1
        self.packetNumber = 0

    #packet logic and other protocol logic, building packet headers, payloads, and building communicaiton protocols
    def buildHeader(self, packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize):
        return(
            packetType + "*" +
            action + "*" +
            status + "*" +
            str(packetNumber) + "*"+
            str(TimeStamp) + "*" +
            str(windowSize) + "*" +
            str(payloadSize) + "*" +
            fileName + "*" +
            str(fileSize) + "*****")
        

    def buildPacket(self, header, payload):
        return header + payload 

    def splitHeader(self, header):
        splitHeader = header.split("*")
        return splitHeader[0], splitHeader[1], splitHeader[2], splitHeader[3], splitHeader[4], splitHeader[5], splitHeader[6], splitHeader[7], splitHeader[8],
        
    def splitPacket(self, packet):
        splitPacket = packet.split("*****")
        return splitPacket[0], splitPacket[1]
        
    def getByteSize(self, payload):
        return len(payload.encode('utf-8'))
            
        
    def getFileSize(self, filename):
        f = os.stat(filename)
        return f.st_size
        
    def checkTimeStamp(self, timeStamp):
        timer = time.time()
        diff = timer - float(timeStamp)
        if(diff < 10,0000):
            return True
        else:
            return False
        
    def listen(self):
        while(1):
            command, fileName = self.recievePacket()
            self.sendPacket("ACK", command, "SUCCESS", 1, time.time() , 1, 0, fileName, self.getFileSize(fileName), "Gonna Send")
            print(str(self.getFileSize(fileName)))
            #a = input()
            if command == "GET":
                self.GET(fileName)
            elif command == "PUT":
                self.PUT(fileName)
            else: 
                print("Command not found")
        
    def recievePacket(self):
        try:
            self.socket.settimeout(10)
            packet, self.clientAddr = self.socket.recvfrom(2048)
            self.tries = 0 
            header, payload = self.splitPacket(packet)
            packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize = self.splitHeader(header)
            if(packet not in self.packetTracker):
                self.packetTracker.append(packet)
                if(self.checkTimeStamp(TimeStamp)):
                    if(packetType == "START"):
                        return (action, fileName)
                    elif(packetType == "CLOSE"):
                        return ("DONE", fileName)
                    elif(packetType == "ACK"):
                        return (status, packet)
                    elif(packetType == "MSSG"):
                        return status, packet
                    elif(packetType == "NAK"):
                        return status, packet
                    else:
                        self.sendPacket("ERROR", "ERROR", "FAIL", 0, 0, 0, 0, "None", 0, "INVALID PACKET")
        except timeout:
            print("In timeout idiots!")
            if (self.tries == 8):
                print("Lost Connection")
                sys.exit(1)
            self.socket.sendto(self.lastPacket, self.clientAddr)
            self.tries += 1
            return self.recievePacket()  
        except Exception as e:
            print(str(e))
            a = input()
            self.sendPacket("ERROR", "ERROR", "FAIL", 0, 0, 0, 0, "None", 0, "INVALID PACKET")
            print("ERROR")
            return 
        
    def sendPacket(self, packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize, payload):
        header = self.buildHeader(packetType, action, status, packetNumber, TimeStamp, windowSize, payload, fileName, fileSize) 
        packet = self.buildPacket(header, payload)
        self.lastPacket = packet
        print(packet)
        self.socket.sendto(packet, self.clientAddr)
        return packet        
    
    def GET(self, fileName):
        file = open(fileName, "r")
        fileSize = self.getFileSize(fileName)
        sentPackets = []
        while(1):
            for x in range(self.windowSize):
                payload = file.read(100)
                payloadSize = self.getByteSize(payload)
                sentPackets.append(self.sendPacket("MSSG", "GET", "SUCCESS", self.packetNumber, time.time(), self.windowSize, payloadSize, fileName, fileSize, payload))
                self.packetNumber += 1
            RTTStart = time.time()
            try:
                self.socket.settimeout(.03)
                packet, self.clientAddr = self.socket.recvfrom(2048)
                header, payload = self.splitPacket(packet)
                packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize = self.splitHeader(header)
                if(packetType == "ACK"):
                    print("ACK!")
                    RTTFinish = time.time()
                    print("RTT: " + str(RTTFinish - RTTStart))
                    if(RTTFinish - RTTStart >= 10000):
                        if(self.windowSize > 1):
                            self.windowSize -= 1
                    else:
                        self.windowSize += 1
                    continue 
                elif(packetType == "NAK"):
                    if(self.windowSize > 1):
                            self.windowSize -= 1
                    #self.resendPacket(packetNumber, sentPackets)
            except timeout:
                continue 

                

        
    def PUT(self, file):
        print("PUT")

        


serverAddr = ("", 50000)


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddr)
server = slidingServer(serverSocket)
server.listen()