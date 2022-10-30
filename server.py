from socket import *
from checksum import *
import pickle


imgs = []
pkgCount = 0
server_seqNum = 0
ACK = 255       # ACK IS 8BITS ALL ONES
ServerPort = 3240 # Set the serverport
serverSocket = socket(AF_INET,SOCK_DGRAM) # create UDP socket for server
serverSocket.bind(('127.0.0.1', ServerPort)) # bind socket to port 3230
clientAdd = '127.0.0.1'
print("Server is ready to use")


class CombinePacket: # combine the checksum and seqNum in one pkg
    def __init__(self,  CS_client, seqNum, pkg):
        self.CS_client = CS_client
        self.seqNum = seqNum
        self.pkg = pkg

class ReturnCombinePacket:  # combine the checksum and seqNum and ACK in one
    def __init__(self, CS, server_seqNum, ACK):  #pkg
        self.CS = CS
        self.server_seqNum = server_seqNum
        self.ACK = ACK

while True:
    pkg = serverSocket.recvfrom(20480) # read message from client and get the client address
    comb_pkg, clientAddress = pkg
    comb_pkg = pickle.loads(comb_pkg)
    CS_client = comb_pkg.CS_client
    client_seqNum = comb_pkg.seqNum
    img = comb_pkg.pkg
    # assign sequence number and checksum by removing from the end of img list
    notCorrupt = checksumCheck(img, CS_client)    # calls checksum checker function, returns 1 if no error

    # implement this code block if no data corruption and sequence number matches
    if notCorrupt == 1 and (server_seqNum == client_seqNum):
        print('This pkg is good!')
        imgs.append(img)
        pkgCount += 1
        rece_pkgsCount = 212
        if pkgCount == rece_pkgsCount:
            break
        # below will do make_pkt and udt_send()
        CS = ACK        # CS = checksum of ACK, NEED ACK TO BE 8BITS
        rComb_pkg = ReturnCombinePacket(CS, server_seqNum, ACK)  # sndpkt = make_pkt(0,data,checksum)
        rComb_pkg = pickle.dumps(rComb_pkg)
        serverSocket.sendto(rComb_pkg, clientAddress)  # udt_send()

        server_seqNum = 1 - server_seqNum  # change sequence number
        """"
        msg = str(ACK) + str(server_seqNum)  # '11'
        serverSocket.sendto(msg.encode(), clientAddress)
        server_seqNum = 1 - server_seqNum  #  change sequence number
        # sndpkt contains ACK, sequence number and checksum data to send back to the sender
        """
    #if there is data corruption or sequence number mismatch
    else:
         CS = ACK  # CS = checksum of ACK, NEED ACK TO BE 8BITS
         rComb_pkg = ReturnCombinePacket(CS, server_seqNum, ACK)  # sndpkt = make_pkt(0,data,checksum)
         rComb_pkg = pickle.dumps(rComb_pkg)
         serverSocket.sendto(rComb_pkg, clientAddress)  # udt_send()

with open('assemble_img.jpg', 'wb') as recv_image:
    #del imgs[0]
    recv_image.write(bytearray(b''.join(imgs)))
    recv_image.close()
