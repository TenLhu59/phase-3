from socket import *
import os
from checksum import *
import pickle
import base64
buffersize = 2048
HOST = '127.0.0.1'  # It is local UDP
ServerPort = 3240 # set serverport
pktCount = 0
seqNum = 0
clientSocket = socket(AF_INET,SOCK_DGRAM) # create UDP socket for client


def mk_pkg(img_path):
    img_len = os.path.getsize(img_path)
    with open(img_path,'rb') as bmp:
        packets = []
        packets_num = img_len//buffersize+2 ## one is for total_pkg, one is just in case fill buffer vacancy
        for i in range(packets_num):
            packets.append(bmp.read(buffersize))  # reference from TA Bhargavi
    return packets

def isACK(CheckS, sequence, acknow, trackSeq):
    if CheckS == acknow and sequence == trackSeq:
        return 1
    else:
        return 0

class CombinePacket: # combine the checksum and seqNum in one pkg
    def __init__(self,  CS_client, seqNum, pkg): #pkg
        self.CS_client = CS_client
        self.seqNum = seqNum
        self.pkg = pkg


class ReturnCombinePacket: # combine the checksum and seqNum and ACK in one
    def __init__(self,  CS, server_seqNum, ACK): #pkg
        self.CS = CS
        self.server_seqNum = server_seqNum
        self.ACK = ACK

# Ref:https://stackoverflow.com/questions/48974070/object-transmission-in-python-using-pickle
# Ref:https://stackoverflow.com/questions/53576851/socket-programming-in-python-using-pickle


pkgs = mk_pkg('./back.jpg')


# packets to the server
for pkg in pkgs:
    # transition from wait for call 0 to wait for ACK 0
    # To be specify,ACK = 1 means ACK ,ACK = 0 means NAK
    # print(pkg)

    CS_client = checksumGen(pkg)

    comb_pkg = CombinePacket(CS_client, seqNum, pkg)    # sndpkt = make_pkt(0,data,checksum)
    comb_pkg = pickle.dumps(comb_pkg)
    clientSocket.sendto(comb_pkg, (HOST, ServerPort))  # udt_send()

    # wait for server to send back reply
    rComb_pkg, serverAddress = clientSocket.recvfrom(buffersize)
    rComb_pkg = pickle.loads(rComb_pkg)
    CS = rComb_pkg.CS
    RseqNum = rComb_pkg.server_seqNum
    ACK = rComb_pkg.ACK

    # remove checksum, sequence number and ACK date from the packet
    #ACK = int(recievedMsg[0])
    #server_seqNum = int(recievedMsg[1])
    #print(f"Received ACK = {ACK},sequence_number = {server_seqNum}")
    #server_seqNum = 1 - server_seqNum

    while isACK(CS, RseqNum, ACK, seqNum) == 0: # isACK function checks if ACK is corrupt and the sequence number matches
        CS_client = checksumGen(pkg)
        comb_pkg = CombinePacket(CS_client, seqNum, pkg)    # sndpkt = make_pkt(0,data,checksum)
        comb_pkg1 = pickle.dumps(comb_pkg)
        clientSocket.sendto(comb_pkg1, (HOST, ServerPort))  # send packets to server udt_send()
        # send packets to server

        # wait for server to send back reply
        """
        recievedMsg, serverAddress = clientSocket.recvfrom(buffersize)
        recievedMsg = recievedMsg.decode()
        # remove checksum, sequence number and ACK date from the packet
        ACK = int(recievedMsg[0])
        server_seqNum = int(recievedMsg[1])
        print(f"Received ACK = {ACK},sequence_number = {server_seqNum}")
        server_seqNum = 1 - server_seqNum
        """
        # receive acknowledgement from server
        rComb_pkg, serverAddress = clientSocket.recvfrom(buffersize)
        rComb_pkg = pickle.loads(rComb_pkg)
        CS = rComb_pkg.CS
        RseqNum = rComb_pkg.RseqNum
        ACK = rComb_pkg.ACK
    # if the packet sent was corrupted or ack is not aligned, send the same packet again

    seqNum = 1 - seqNum     # change sequence number

clientSocket.close()







