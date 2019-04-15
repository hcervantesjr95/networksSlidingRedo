#! /bin/python
from socket import *
import sys, time 

class slidingServer():

    def __init__(self, socket):
        self.socket = socket
        self.clientAddr= ("localhost", 50001)
        self.packetNum = 0
        self.fileName = ""
        self.fileNum = 0
        self.windowSize = 1
        self.packetChecker = []
    
    def buildHeader(self, packetType, action, timeStamp, status, windowSize,windowCounter, packetCounter, payload, fileName):
        return (packetType + "*" + 
        action + "*" + 
        str(timeStamp) + "*" + 
        status + "*" + 
        str(windowSize) + "*" + 
        str(windowCounter) + "*" + 
        str(packetCounter) + "*" + 
        str(self.getPayloadSize(str(payload))) + "*" + 
        fileName + "***")
    
    def buildPacket(self, header, payload):
        return header + payload  
    
    def getHeaderSize(self, header):
        return len(header.encode('utf-8'))

    def getPayloadSize(self, payload):
        return len(payload.encode('utf-8'))

    def splitPacket(self, packet):
        packet = packet.split("***")
        return packet[0], packet[1]
    
    def splitHeader(self, header):
        header = header.split("*")
        return header[0], header[1], header[2], header[3], header[4], header[5], header[6], header[7], header[8]
#[packetType*action*timestamp*status*windowSize*windowCounter*packetCounter*payloadSize*fileName***payload]    
    ################################### COMMUNICATION LOGIC ################################## 

    def sendPacket(self, packetType, action, timeStamp, status, windowSize, windowCounter, packetCounter, payload, fileName):
        header = self.buildHeader(packetType, action, timeStamp, status, windowSize, windowCounter, packetCounter, payload, fileName)
        packet = self.buildPacket(header, payload)
        #print("sending packet with payload" + packet)
        self.socket.sendto(packet, self.clientAddr)
        return packet

    def checkTimeStamp(self, timeStamp):
        timer = time.time()
        diff = timer - float(timeStamp)
        if(diff < 10,0000):
            return True
        else:
            return false

    def receivePacket(self):
        try:
            while(1):
                print("waiting for packet")
                #self.socket.settimeout(0)
                packet, self.clientAddr = self.socket.recvfrom(2048)
                if(packet == ""):
                    print("TIMED OUT")
                    break
                header, payload = self.splitPacket(packet)
                packetType, action, timeStamp, status, windowSize, windowCounter, packetCounter, payloadBytes, fileName = self.splitHeader(header)
                if(self.checkTimeStamp(timeStamp)):
                    if(packet not in self.packetChecker or packetType == "ERROR"):
                        self.packetChecker.append(packet)
                        if(packetType == "START"):
                            return (action, fileName)
                        elif(packetType == "CLOSE"):
                            return ("DONE", fileName)
                        elif(packetType == "ACK"):
                            return(status, packet)
                        elif(packetType == "MSSG"):
                            return (header, payload)
                        elif(packetType == "ERROR"):
                            print("There was an Error")
                            return("DONE", payload)
                        else:
                            print("ERROR INVALID PACKET FORMAT")
                            header = self.buildHeader("ERROR", "ERROR", "0.0", "FAILED", 0, 0, 0, 0, "FAILED")
                            packet = buildPacket(header, "INVALID PACKET")
                            self.socket.sendto("PACKET NOT KNOWN. TERMINATING", self.clientAddr)
                            return("DONE", payload)
        except  Exception as e:
            print(str(e))
            header = self.buildHeader("ERROR", "ERROR", "0:0:0:0", "FAILED", 0, 0, 0, 0, "FAILED")
            packet = self.buildPacket(header, "INVALID PACKET")
            #self.socket.sendto("PACKET NOT KNOWN. TERMINATING", self.clientAddr)
            return("DONE", packet)


    def POST(self):
        try:
            print("getting file")
            file = open(self.fileName, "w")
            packet = ""
            self.socket.sendto("GET" + fileName, clientAddrPort)
            while(packet != "DONE"):
                packet, self.clientAddr = self.sock.recvfrom(100)
                header, payload = packet.split("*****")
                packetNum, jobTYpe, packetType, fileName, payloadBytes = header.split(":")
                if(payloadBytes == self.getPayloadSize(payload)):
                    if(packetNum == self.packetNum):
                        file.write(payload)
                        self.sendPacket("CLOSE","GET", time.time)
                        self.doSendAck("SUCCESS", packetNum, fileName)
                        self.packetNum += 1
                    else:
                        self.doSendAck("SUCCESS", packetNum, fileName) 

                else:
                    self.doSendAck("FAIL", packetNum + 1, fileName)
        except ex:
            print(ex)
            return 

    def resendPackets(self, packet, window):
         header, payload = self.splitPacket(packet)
         packetType, action, timeStamp, status, windowSize, windowCounter, packetCounter, payloadBytes, fileName = self.splitHeader(header)
         self.packetNum = int(packetCounter)
         print("resending: "+ window[self.packetNum])
         self.socket.sendto(window[self.packetNum], self.clientAddr)
         self.packetNum += 1


            


    def GET(self):
        try:
            file = open(self.fileName, "r")
            windowCounter = 0
            Done = False
            while(not Done):
                window = {}
                windowCounter = 0
                for x in range(0, self.windowSize):
                    payload = file.read(100)
                    if(payload == ""):
                        self.sendPacket("CLOSE","GET", time.time(), "SUCCESS", 0, 0, 0, "DONE", self.fileName)
                        self.packetNum = 0
                        file.seek(0)
                        file.close()
                        Done = True 
                        break
                    self.packetNum += 1
                    windowCounter += 1
                    window[str(self.packetNum)] = self.sendPacket("MSSG", "GET", time.time(), "SUCCESS", self.windowSize, x, self.packetNum, payload, self.fileName)
                if(not Done):
                    while(1):
                        status, packet = self.receivePacket()
                        print(str(status))
                        if(status == "SUCCESS"):
                            print("SUCCESS")
                            self.windowSize += 1
                            break
                        elif(status == "FAIL"):
                            print("FAIL")
                            # resending of packets needs work 
                            self.resendPackets(packet, window)
                            if(self.windowSize > 1):
                                self.windowSize -= 1
        except Exception as e:
            print(e)
            return

    def listen(self):
        while(1):
            print("Listening on the server")
            action, fileName = self.receivePacket()
            self.fileName = fileName
            if(action == "GET"):
                print("GET " + fileName)
                self.GET()
            elif(action == "PUT"):
                print("PUT " + fileName)
                self.PUT()


                
serverAddr = ("", 50001)
'''
def usage():
    print "usage: %s [--serverPort <port>]"  % sys.argv[0]
    sys.exit(1)

try:
    args = sys.argv[1:]
    while args:
        sw = args[0]; del args[0]
        if sw == "--serverPort":
            serverAddr = ("", int(args[0])); del args[0]
        else:
            print "unexpected parameter %s" % args[0]
            usage()
except:
    usage()
'''
print ("binding datagram socket to %s" % repr(serverAddr))

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddr)
print("ready to receive")
server = slidingServer(serverSocket)
server.listen()
    
                