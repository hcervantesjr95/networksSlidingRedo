from socket import *
import sys, re, os, time 





'''
[packetType*action*timestamp*status*windowSize*windowCounter*packetCounter*payloadSize*fileName***payload]
'''
class slidingClient():

    def __init__(self, socket, files, serverAddr):
        self.socket = socket
        self.serverAddr= serverAddr
        self.packetNum = 0
        self.files = files
        self.fileNum = 0
        self.windowSize = 1
        self.packetChecker = [] 
        self.lastPacket = ""
    
    ################################### PACKET LOGIC ##################################
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

    def sendPacket(self, packetType, action, timeStamp, status, windowSize,windowCounter, packetCounter, payload, fileName):
        header = self.buildHeader(packetType, action, timeStamp, status, windowSize,windowCounter, packetCounter, payload, fileName)
        packet = self.buildPacket(header, payload)
        print("sending packet with payload" + packet)
        self.socket.sendto(packet, self.serverAddr)

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
                self.socket.settimeout(8.0)
                packet, self.serverAddr = self.socket.recvfrom(2048)
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
                            self.socket.sendto("PACKET NOT KNOWN. TERMINATING", self.serverAddr)
                            return("DONE", payload)
        except TimeoutError:
             
        except  Exception as e:
            print(str(e))
            header = self.buildHeader("ERROR", "ERROR", "0:0:0:0", "FAILED", 0, 0, 0, 0, "FAILED")
            packet = self.buildPacket(header, "INVALID PACKET")
            self.socket.sendto("PACKET NOT KNOWN. TERMINATING", self.serverAddr)
            return("DONE", packet)

#[packetType*action*timestamp*status*windowSize*windowCounter*packetCounter*payloadSize*fileName***payload]
################################### FILE PROCESSING LOGIC ##################################
    def GET(self, fileName):
        print("getting file")
        file = open(fileName, "w+")
        self.sendPacket("START", "GET", time.time() , "NONE", 0 , 0, 0, "NONE", fileName)
        windowCount = 1
        self.packetNum = 1
        while(1):
            header, payload  = self.receivePacket()
            if(header == "DONE"):
                break
            packetType, action, timeStamp, status, windowSize, windowCounter, packetCounter, payloadBytes, fileName = self.splitHeader(header)
            if(int(payloadBytes) == self.getPayloadSize(payload)):
                if(self.packetNum == int(packetCounter)):
                    file.write(payload)
                    if(windowCount == self.windowSize):
                        self.sendPacket("ACK", "GET", time.time() , "SUCCESS", self.windowSize , windowCount, self.packetNum, "GOOD", fileName)
                        windowCount = 1
                        self.packetNum += 1
                        self.windowSize += 1
                    else:
                        windowCount += 1
                        self.packetNum += 1
                else:
                    print("EXPECTED PACKET: " + str(self.packetNum) + " GOT: " + packetCounter)
                    self.packetChecker.remove(header + "***" + payload)
                    self.sendPacket("ACK", "GET", time.time(), "FAIL", self.windowSize, windowCount, self.packetNum, "PACKET NOT EQUAL", fileName)
                    if(self.windowSize > 1):
                        self.windowSize -= 1
            else:
                print("BYTES ARE MISSING FOR PACKET: " + packetCounter)
                self.packetChecker.remove(header + "***" + payload)
                self.sendPacket("ACK", "GET", time.time(), "FAIL", self.windowSize, windowCount, self.packetNum, "BYTES NOT EQUAL", fileName)
                if(self.windowSize > 1):
                    self.windowSize -= 1
        file.close()



        




    def POST(self, file):
        print("sendingFile")
        self.sock.sendto( "POST", self.serverAddr)
    
    def startGet(self, files):
        for x in range(len(files)):
            self.GET(files[x])
    
    def startPost(self, files):
        for x in range(len(files)):
            self.POST(self, files[x])
    
'''
def usage():
    print "usage: [--serverAddr host:port] [--commnad GET (or POST)] [--file file1 file2 ...]" 
    sys.exit(1)
'''
serverAddr = ('localhost' , 50000)
files = ["Hello.txt"]
command = "GET"

'''
try:
    args = sys.argv[1:]
    while args:
        sw = args[0]; del args[0]
        if sw == "--serverAddr":
            addr, port = re.split(":", args[0]); del args[0]
            serverAddr = (addr, int(port))
        elif sw == "--files":
            files = re.split(" ", args[0]); del args[0]
        elif sw == "--command":
            command = args[0]
        else:
            print "unexpected parameter %s" % args[0]
            usage()
except:
    usage()
'''

clientSocket = socket(AF_INET, SOCK_DGRAM)
client = slidingClient(clientSocket, files, serverAddr)
if command == "GET":
    client.startGet(files)
elif command == "POST":
    client.startPOST(files)
else:
    usage()
    print ("Modified message from %s is <%s>" % (repr(serverAddrPort), modifiedMessage))
