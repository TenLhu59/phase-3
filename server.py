from socket import *
from checksum import *
import pickle
import random


imgs = []
pkgCount = 0
server_seqNum = 0
previous_seqNum = 1  # place holder
error_per = 5
ACK = 255       # ACK IS 8BITS ALL ONES
rece_pkgsCount = 286
ServerPort = 3240 # Set the serverport
serverSocket = socket(AF_INET,SOCK_DGRAM) # create UDP socket for server
serverSocket.bind(('127.0.0.1', ServerPort)) # bind socket to port 3230
clientAdd = '127.0.0.1'
print("Server is ready to use")

class CombinePacket: # combine the checksum and seqNum in one pkg
    def __init__(self,  CS_client, seqNum, pkg, u_input, error_percent):
        self.CS_client = CS_client
        self.seqNum = seqNum
        self.pkg = pkg
        self.u_input = u_input
        self.error_percent = error_percent

class ReturnCombinePacket:  # combine the checksum and seqNum and ACK in one
    def __init__(self, CS, server_seqNum, ACK):  #pkg
        self.CS = CS
        self.server_seqNum = server_seqNum
        self.ACK = ACK

while True:
    pkt = serverSocket.recvfrom(20480) # read message from client and get the client address
    comb_pkg, clientAddress = pkt
    comb_pkg = pickle.loads(comb_pkg)
    CS_client = comb_pkg.CS_client
    client_seqNum = comb_pkg.seqNum
    user_input = comb_pkg.u_input
    error_per = comb_pkg.error_percent
    img = comb_pkg.pkg

    # to add bit error in data. Bits are flipped
    if user_input == 3 and error_per > random.randint(0, 100):
        #print(CS_client)
        CS_client = ~CS_client & 0xFFFF     # bits flipped
        #print(CS_client)

    notCorrupt = checksumCheck(img, CS_client)    # calls checksum checker function, returns 1 if no error
    # implement this code block if no data corruption and sequence number matches
    if notCorrupt == 1 and (server_seqNum == client_seqNum):
        #print('This pkg is good!')
        imgs.append(img)
        pkgCount += 1
        # below will do make_pkt and udt_send()
        CS = ACK        # CS = checksum of ACK, NEED ACK TO BE 8BITS
        rComb_pkg = ReturnCombinePacket(CS, server_seqNum, ACK)  # sndpkt = make_pkt(0,data,checksum)
        rComb_pkg = pickle.dumps(rComb_pkg)
        serverSocket.sendto(rComb_pkg, clientAddress)  # udt_send()
        previous_seqNum = server_seqNum
        server_seqNum = 1 - server_seqNum  # change sequence number

    # if there is data corruption or sequence number mismatch
    else:   # send the same ACK packet with the sequence number again
        # below if else is for debugging only
        """
        if notCorrupt == 0:
            print("Corrupt data")
        else:
            print("Duplicate packet")
        """
        CS = ACK  # CS = checksum of ACK, NEED ACK TO BE 8BITS
        rComb_pkg = ReturnCombinePacket(CS, previous_seqNum, ACK)  # sndpkt = make_pkt(0,data,checksum)
        rComb_pkg = pickle.dumps(rComb_pkg)
        serverSocket.sendto(rComb_pkg, clientAddress)  # udt_send()

    if pkgCount == rece_pkgsCount:
        print("Image received")
        with open('assemble_img.jpg', 'wb') as recv_image:
            # del imgs[0]
            recv_image.write(bytearray(b''.join(imgs)))
            recv_image.close()
        pkgCount = 0
