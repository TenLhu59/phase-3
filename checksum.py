import numpy as np

# checksum generator


def checksumGen(pkg):
    final = np.array([],dtype=np.int)
    for i in range(0, len(pkg), 2):
        w = pkg[i]  # pkg[0]
        q = pkg[i + 1]  # pkg[1]
        r = w << 8  # Make the first 8bit data left shift 8 space
        result = r + q  # Get the 16bit data
        final = np.append(final, result)
    finalresult = 0
    for num in final:
        finalresult += num
        if finalresult >= 65536:
            finalresult -=65535   # wraparound overflow reference:https://stackoverflow.com/questions/64997503/binary-addition-carry-and-overflow-in-python
    return finalresult      # lets flip the bits on the checksum checker function

# checksum checker


def checksumCheck(pkg, CS_client):      # checksum is the checksum received in the header of the received data from the sender
    CS_server = checksumGen(pkg)           # call checksum generator fucntion to add all the data
    CS_server = ~CS_server & 0xFFFF       # flips the bits so the addtion in the next line can be all 1s
    if (CS_client + CS_server) == 65535:     # if the all 16bits are 1s (65535) then no error an return 1
        return 1
    else:                                   # otherwise return 0 to indicate error
        return 0