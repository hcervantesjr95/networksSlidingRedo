from socket import *
import os, time, sys 



class ErrorQueue():

    def __init__(self):
        self.head = None
    
    def enqueue(self, packet, number):
        if(self.head is None):
            self.head = Node(packet, number)
            return self.head
        temp = self.head
        while(temp.next != None):
            temp = temp.next
        temp.next = Node(packet, number)
        
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
        self.head.number = self.head.next.number 
        self.head.next = self.head.next.next
        temp = None
        return self.head, deletedPacket

    def empty(self):
        return self.head == None
    
    def printQueue(self, node):
        while node != None:
            print(node.packet)
            node = node.next
        print(" ")
    
    def checkPacket(self, number):
        temp = self.head
        while temp != None:
            if(temp.number == number):
                return True
            temp = temp.next 
        return False
    def expectedPacket(self, packetNumber):
        return self.header.number == packetNumber
    
    def remove(self, number):
        if(self.head == number):
            if(self.head.next == None):
                self.head = None 
            else:
                self.head.packet = self.head.next.packet 
                self.head.number = self.head.next.number
                self.head.next = self.head.next.next
        
        else:
            temp = self.head
            while temp != None:
                if(temp.number == number):
                    if(temp.next != None):
                        t = temp
                        temp.packet = t.next.packet
                        temp.number = t.next.number
                        temp.next = t.next.next
                    else:
                        temp.number = None 
                        temp.packet = None 
                        temp = None
                        break 
                temp = temp.next 
        
        print(str(self.head == None))
        return self.head  
                



class Node():
    def __init__(self, packet, number):
        self.packet = packet
        self.number = number 
        self.next = None 
    
    def getNext(self):
        return self.next
    
    def getWord(self):
        return self.word
q = ErrorQueue()
head = q.enqueue("packet1", 1)
head = q.enqueue("packet2", 2)
head = q.enqueue("packet10", 10)
print(q.checkPacket("packet1"))
q.printQueue(head)
d = q.remove(2)
print(q.checkPacket("packet1"))
q.printQueue(head)
d = q.remove(1)
q.printQueue(head)
print("removing 10")
d = q.remove(10)
q.printQueue(head)
print(q.empty())