# Initial hash values to help set the output size.
# Simply different iterations of counting represented in in little-endian hexadecimal converted to big-endian
initial_hash_value = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]


def SHA1(message): 
    # Implementation based on NIST.FIPS.180-4

    # Get the K values
    K = Fill_Constants()
    H = initial_hash_value

    # Pad the message
    padded_message = Preprocess(message)
    # Get the number of cycles needed
    N = (len(padded_message) * 8) / 512

    for i in range(1, N+1):
        W = []

        # TODO: Reformat this to be readable
        # Prepare the message Schedule:
        for t in range(80):
            if t <= 15:
                # M_sub-t_exp-i
                W.extend([ int(padded_message[ (32 * t) : (32 * (t + 1)) ], 2)  ])
            else:
                W.extend([ Left_Rotate( W[t - 3] ^ W[t - 8] ^ W[t - 14] ^ W[t - 16], amount=1, bitSize=32) ])

        # Set the five working variables    
        a = H[0]
        b = H[1]
        c = H[2]
        d = H[3]
        e = H[4]

        # Use a different function for each t values
        for t in range(80):
            if t <= 19:
                f = Choose
            elif t <= 39:
                f = Parity
            elif t <= 59:
                f = Majority
            else:
                f = Parity

            T = (Left_Rotate(a, amount=5, bitSize=32) + f(x=b, y=c, z=d) + e + K[t] + W[t]) % (2 ** 32)
            e = d
            d = c
            c = Left_Rotate(b, amount=30, bitSize=32)
            b = a
            a = T

        # Compute the ith intermediate hash value 
        H[0] = (a + H[0]) % (2 ** 32)
        H[1] = (b + H[1]) % (2 ** 32)
        H[2] = (c + H[2]) % (2 ** 32)
        H[3] = (d + H[3]) % (2 ** 32)
        H[4] = (e + H[4]) % (2 ** 32)
    
    # Append the H values to form the final result.
    Final_Message = [format(x, '08x') for x in H]
                

def Left_Rotate(input, amount, bitSize=32):
    # Shift the input bits left by amount circularly and ensure no padding bits are added, bitwise OR that value with the input shifted to the right by the number of total bits
    # For Example: 11110000, 1 -> 11100001
    # For Example: 10101010, 1 -> 01010101
    # For Example: 11110000, 3 -> 10000111
    return (input << amount & (2**bitSize - 1)) | (input >> (bitSize - amount))

def Choose(x, y, z):
    # For t values 0 -> 19
    # x input chooses if the output is based on y or z
    # For example: x= 1111, y= 1011, z= 0010 returns 1011
    # For example: x= 0000, y= 1011, z= 0010 returns 0010
    return (x & y) ^ (~x & z)

def Parity(x, y, z):
    # For t values 20 -> 39, 60 -> 79
    # Determines the parity of each bit of the three inputs
    # For Example: x= 1111, y= 1011, z= 0010 returns 0110
    return x ^ y ^ z

def Majority(x, y, z):
    # For t values 40 -> 59
    # Gives the Majority bit value by checking all three inputs - 1 if 2 or 3 bits are 1
    # For Example: x= 1111, y= 1011, z= 0010 returns 1011
    return (x & y) ^ (x & z) ^ (y & z)

def Fill_Constants():
    # Initial Values are based on Binary Square roots
    K = [None]*80
    for t in range(80):
        if t <= 19:
            # Root 2
            K[t] = 0x5a827999
        elif t <= 39:
            # Root 3
            K[t] = 0x6ed9eba1
        elif t <= 59:
            # Root 5
            K[t] = 0x8f1bbcdc
        elif t <= 79:
            # Root 10
            K[t] = 0xca62c1d6
    return K

def Get_Bit_Count(message:str):
    # Gets the total number of bits in a string assuming 8 bits per byte, with one byte per letter
    return len(message.encode('ascii')) * 8

def get_binary_list(message:str)-> list:
    # convert the string to ascii bytes
    m_bytes = message.encode('ascii')
    # format the bytes into bits
    return [format(x, '08b') for x in m_bytes]

def Preprocess(message):
    # First pad the message to a length of a multiple of 512 bits\
    bit_count = Get_Bit_Count(message)
    padding = 447 - bit_count
    bit_message = get_binary_list(message)
    # Append a 1, then fill the rest with 0's until mod 512 by appending blocks of 8 zeros.
    bit_message.append('10000000')
    for i in range(((padding+1)/8)-1):
        bit_message.append('00000000')
    # Finally append the length of the message in binary
    bit_message.append(format(bit_count, '08b'))
    return bit_message