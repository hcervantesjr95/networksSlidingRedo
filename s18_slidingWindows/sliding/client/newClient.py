from socket import *
import os, time, sys 

class slidingClient():

    def __init__(self, socket, serverAddr):
        self.socket = socket 
        self.serverAddr = serverAddr
        self.packetTracker = []
        self.packetsReceived = []
        self.lastPacket = ""
        self.tries = 0
        self.fileSize = 0
        self.windowSize = 0
        self.packetNumber = 0

    def reset(self):
        self.packetTracker = []
        self.packetsReceived = []
        self.lastPacket = ""
        self.tries = 0
        self.fileSize = 0
        self.windowSize = 0
        self.packetNumber = 0

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
        
    def recievePacket(self):
        try:
            self.socket.settimeout(5)
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
            if (self.tries == 8):
                print("Lost Connection")
                sys.exit(1)
            self.socket.sendto(self.lastPacket, self.serverAddr)
            self.tries += 1
            return self.recievePacket()              
        except Exception as e:
            print(str(e))
            # a = input()
            self.sendPacket("ERROR", "ERROR", "FAIL", 0, 0, 0, 0, "None", 0, "INVALID PACKET")
            print("ERROR")
            return 
        
    def sendPacket(self, packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize, payload):
        header = self.buildHeader(packetType, action, status, packetNumber, TimeStamp, windowSize, payload, fileName, fileSize) 
        packet = self.buildPacket(header, payload)
        errorBuffer = {} 
        print(packet)
        self.socket.sendto(packet, self.serverAddr)
        return packet 
        
    def startHandshake(self, fileName, command):
        while(1):
            self.sendPacket("START", command, "SUCCESS", 0, time.time(), 0, 0, fileName, 0, "Ready to start")
            status, packet = self.recievePacket()
            header, payload = self.splitPacket(packet)
            packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize = self.splitHeader(header)
            if(status == "SUCCESS"):
                self.windowSize = int(windowSize)
                self.packetNumber = int(packetNumber)
                self.fileSize = int(fileSize)
                if(int(fileSize) % 100 != 0):
                    self.packetsReceived = ([0] * ((int(fileSize) / 100) + 1))
                else:
                    self.packetsReceived = ([0] * (int(fileSize) / 100))
                    a = input()
                return 
    
    def allPacketsArrived(self):
        for x in range(len(self.packetsReceived)):
            if(self.packetsReceived[x] == 0):
                return False
        return True 


    def GET(self, fileName):
        self.startHandshake(fileName, "GET")
        windowCounter = 0
        lastACKNum = 0
        errorQ = ErrorQueue()
        while(not self.allPacketsArrived()):
            status, packet = self.recievePacket()
            header, payload = self.splitPacket(packet)
            packetType, action, status, packetNumber, TimeStamp, windowSize, payloadSize, fileName, fileSize = self.splitHeader(header)
            if(packetType == "MSSG"):
                # add expecting packet to the error queue
                if(self.packetNumber != packetNumber):
                        lastACKNum = self.packetNumber
                        errorQ.enqueue((self.sendPacket("NAK", "GET", "FAILED", self.packetNumber, 0.0, self.windowSize, 0, fileName, self.fileSize, "MISSING PACKET")), lastACKNum)
                #if errorQ is empty, send ACK 
                if(errorQ.empty()): 
                    self.sendPacket("ACK", "GET", "SUCCESS", self.packetNumber, time.time(), self.windowSize, 100, fileName, self.fileSize, "GOOD")
                self.packetsReceived[int(packetNumber)] = payload
                self.packetNumber += 1
        print("writing to file")
        file = open(fileName, "w+")
        for x in range(len(self.packetsReceived)):
            file.write(self.packetsReceived[x])
        file.close()
        self.reset()
            
             
    
    def PUT(self, fileName):
        self.startHandshake(fileName, "PUT")

def start():
    serverAddr = ('localhost' , 50000)
    files = ["hamlet.txt"]
    command = "GET"
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    client = slidingClient(clientSocket, serverAddr)
    if(command == "GET"):
        client.GET(files[0])
    else:
        client.PUT(files[0])

start()