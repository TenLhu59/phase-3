from socket import *
import os
from checksum import *
import pickle
import time
import random
buffersize = 2048
HOST = '127.0.0.1'  # It is local UDP
ServerPort = 3240 # set serverport
seqNum = 0
user_input = 0
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
    def __init__(self,  CS_client, seqNum, pkg, u_input, error_percent): #pkg
        self.CS_client = CS_client
        self.seqNum = seqNum
        self.pkg = pkg
        self.u_input = u_input
        self.error_percent = error_percent


class ReturnCombinePacket: # combine the checksum and seqNum and ACK in one
    def __init__(self,  CS, server_seqNum, ACK): #pkg
        self.CS = CS
        self.server_seqNum = server_seqNum
        self.ACK = ACK


# Ref:https://stackoverflow.com/questions/48974070/object-transmission-in-python-using-pickle
# Ref:https://stackoverflow.com/questions/53576851/socket-programming-in-python-using-pickle

while True:
    print("Choose which option to implement:")
    print("1 - No loss/bit-errors")
    print("2 - ACK packet bit-error")
    print("3 - Data packet bit-error")
    print("0 - Quit")
    user_input = input()
    user_input = int(user_input)
    if user_input == 0:
        break
    for x in range(0, 65, 5):       # loop to increment the error percentage in one go
        error_per = x
        start = time.time()
        pkgs = mk_pkg('./back.jpg')


        # packets to the server
        for pkg in pkgs:
            # transition from wait for call 0 to wait for ACK 0

            while True:
                CS_client = checksumGen(pkg)
                comb_pkg = CombinePacket(CS_client, seqNum, pkg, user_input, error_per)    # sndpkt = make_pkt(0,data,checksum)
                comb_pkg = pickle.dumps(comb_pkg)
                clientSocket.sendto(comb_pkg, (HOST, ServerPort))  # send packets to server udt_send()
                # send packets to server

                # wait for server to send back reply
                rComb_pkg, serverAddress = clientSocket.recvfrom(buffersize)
                rComb_pkg = pickle.loads(rComb_pkg)
                CS = rComb_pkg.CS
                RseqNum = rComb_pkg.server_seqNum
                ACK = rComb_pkg.ACK
                if user_input == 2 and error_per > random.randint(0, 100):
                    ACK = 254  # corrupt the ack to 254
                    #print('ACK packet wrong, please transmit again')
                # receive acknowledgement from server

                # if statement breaks from the while loop when the correct data is received from receiver
                if isACK(CS, RseqNum, ACK, seqNum) == 1:
                    break
            # if the packet sent was corrupted or ack is not aligned, send the same packet again

            seqNum = 1 - seqNum     # change sequence number
        end = time.time()

        # To compute execution time
        total_time = end - start
        print("Total time for " + str(x) + "% error: " + str(total_time))

        # if the option is no loss then no need to run for loop to get all 60 increments
        if user_input == 1:
            break

clientSocket.close()
