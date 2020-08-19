# FIT3155 Assignment 3 Task 2 encoder
# Name: Chong Chiu Gin
# Student ID: 28842022

import heapq
import sys

def zalgo(pat, windowSize, bufferSize):
    """
    this function finds the length of the longest substring at each position that matches the prefix
    Time complexity: O(m) - m for length of pattern
    Space complexity: O(m) - length of z-array
    :param pat: the pattern,
           windowSize: the size of window in this pattern,
           buffersSize: the size of buffer in this pattern
    :return: the length of longest matching substring in window and it's offset position
    """

    m = len(pat)
    zArr = [0 for x in range(m)]  # initialising Z-array

    l = 0           # LEFT of most right z-box
    r = 0           # RIGHT of most right z-box
    zArr[0] = m     # the first index of Z-array will always be length of pattern

    max_length = 0
    max_position = 0
    start = bufferSize + 1
    end = bufferSize + 1 + windowSize
    # just compute until window, can skip anything else after that
    for i in range(1,bufferSize+windowSize+1):

        # case 1: if i lies to the right of r
        if i > r:
            preNum = 0      # index starter for prefix pointer
            iNum = i        # index starter for i pointer
            while iNum < m and pat[iNum] == pat[preNum]:
                iNum += 1
                preNum += 1
            zArr[i] = preNum
            if zArr[i] != 0:  # shifting the LEFT and RIGHT for new z-box window
                l = i
                r = iNum - 1

        # case 2: if i lies between l and r
        else:
            k = i-l             # index pointer for the matching prefix
            remaining = r-i+1   # remaining is the number of characters from current position of i to the right of z-box

            # case 2a
            if zArr[k] < remaining:
                zArr[i] = zArr[k]

            # case 2b
            elif zArr[k] > remaining:
                zArr[i] = remaining

            # case 2c  zArr[i] == remaining
            else:
                preNum = remaining
                iNum = i + remaining
                count = 0
                while iNum < m and pat[iNum] == pat[preNum]:
                    iNum += 1
                    preNum += 1
                    count += 1
                zArr[i] = zArr[k] + count
                l = i
                r = iNum - 1

        # store longest length and its position
        if zArr[i] >= max_length and start <= i and i < end :
            max_length = zArr[i]
            max_position = i

    buffPoint = bufferSize+windowSize+1
    offset = buffPoint - max_position
    return max_length, offset


def huffman_encoding(chars, frequencyCounter, huffmanEncoding):
    """
    function to find huffman encoding for all unique chars
    :param chars: the set of unique chars
    :param frequencyCounter: table storing all the number of occurence of char
    :param huffmanEncoding: table to store the chars' huffman encoding
    :return: huffmanEncoding
    """

    # build heap array
    heapArr = []
    for char in chars:
        heapArr.append([frequencyCounter[ord(char)],len(char) , char])

    #heapify the heap
    heapq.heapify(heapArr)

    # if there's only one unique char in the text
    if len(heapArr) == 1:
        index = ord(heapArr[0][2])
        huffmanEncoding[index] = '0'

    while len(heapArr) > 1:
        # pop two times
        first = heapq.heappop(heapArr)
        second = heapq.heappop(heapArr)

        for char in first[2:]:
            index = ord(char)
            if huffmanEncoding[index] is not None:
                huffmanEncoding[index] = '0' + huffmanEncoding[index]
            else:
                huffmanEncoding[index] = '0'

        for char in second[2:]:
            index = ord(char)
            if huffmanEncoding[index] is not None:
                huffmanEncoding[index] = '1' + huffmanEncoding[index]
            else:
                huffmanEncoding[index] = '1'

        chars = first[2:] + second[2:]
        heapq.heappush(heapArr,[first[0]+second[0]] + [len(chars)] + first[2:] + second[2:] )

    return huffmanEncoding


def elias_encoding(num):
    """
    get elias encoding of num
    :param num: the number to encode
    :return: the encoded elias number
    """
    # cannot encode negative and non integer
    if num < 1:
        return None

    # get binary of num
    eliasEncoding = decimal2binary(num)

    # get length of binary of num
    length = len(eliasEncoding)

    while length > 1:
        length = length - 1
        binaryLength = decimal2binary(length)
        binaryLength = '0'+binaryLength[1:]
        eliasEncoding = binaryLength + eliasEncoding
        length = len(binaryLength)

    return eliasEncoding

def decimal2binary(num):
    """
    convert num to binary string
    :param num: the decimal number
    :return: the binary string of num
    """
    numBin = bin(num)
    return numBin[2:]

def getLZSSFormat(txt,windowSize, bufferSize):
    """
    get LZSS format fields of txt
    :param txt: the text to be encoded
    :param windowSize: window size
    :param bufferSize: buffer size
    :return: all the format fields
    """
    n = len(txt)

    formatFields = []
    # the first format field is always type '1'
    curFormat = [1,txt[0]]
    formatFields.append(curFormat)

    bufferPointer = 1
    while bufferPointer<n:
        windowPointer = max(bufferPointer-windowSize,0)

        pattern = txt[bufferPointer:bufferPointer+bufferSize]+'$'+txt[windowPointer:bufferPointer+bufferSize]
        zArrBufferSize = bufferSize
        if n-bufferPointer<bufferSize:
            zArrBufferSize = n-bufferPointer
        matchingLength, offset = zalgo(pattern,bufferPointer-windowPointer, zArrBufferSize)

        if matchingLength>=3:
            curFormat = [0,offset,matchingLength]
            formatFields.append(curFormat)
            bufferPointer += matchingLength
        else:
            curFormat = [1, txt[bufferPointer]]
            formatFields.append(curFormat)
            bufferPointer += 1

    return formatFields


def lzss_encode(txt,windowSize, lookaheadSize):
    """
    The main body code
    Encode header and data of txt
    :param txt: the text to be encoded
    :param windowSize: window size
    :param lookaheadSize: buffer size
    :return: the encoded plaintext
    """

    n = len(txt)

    #find number of unique chars in text
    chars = set(txt)
    m = len(chars)

    # find the occurences of each unique char in text
    frequencyCounter = [0 for x in range(128)]
    for i in range(n):
        frequencyCounter[ord(txt[i])] += 1

    # get huffman code for each unique char and store into huffmanEncoding table
    huffmanEncoding = [None for x in range(128)]
    huffmanEncoding = huffman_encoding(chars, frequencyCounter, huffmanEncoding)


    # calls LZSS with window and lookahead buffer for text, uses z-array
    # returns list of format fields
    formatFields = getLZSSFormat(txt,windowSize,lookaheadSize)

    # start encoding header
    plaintext = []
    # elias encode number of unique chars
    plaintext.append(elias_encoding(m))
    for i in range(len(huffmanEncoding)):
        if huffmanEncoding[i] is not None:
            asciiBinary = decimal2binary(i)
            # need to check if asciiBinary is length less than 7, pad the front with zeros if <7
            if len(asciiBinary)<7:
                zeroPads = '0'*(7-len(asciiBinary))
                asciiBinary = zeroPads + asciiBinary
            huffmanCode = huffmanEncoding[i]
            huffmanLength = elias_encoding(len(huffmanCode))
            plaintext.append(asciiBinary + huffmanLength + huffmanCode)

    # encode info
    plaintext.append(elias_encoding(len(formatFields)))
    for i in range(len(formatFields)):
        field = formatFields[i]
        if field[0] == 1:
            huffmanCode = huffmanEncoding[ord(field[1])]
            plaintext.append("1" + huffmanCode)
        else: #field[0] == 0
            plaintext.append("0" + elias_encoding(field[1]) + elias_encoding(field[2]))

    # return header + data
    return "".join(plaintext)

if __name__ == "__main__":

    input_text_file = sys.argv[1]
    windowSize = int(sys.argv[2])
    bufferSize = int(sys.argv[3])

    text = ''
    ftext = open(input_text_file, "r")
    for line in ftext:
        text = line

    bitstring = lzss_encode(text,windowSize,bufferSize)

    byteArr = bytearray()
    for i in range(0,len(bitstring),8):
        currentBits = bitstring[i:i+8]
        if len(currentBits) < 8:
            currentBits = currentBits + ('0'*(8-len(currentBits)))
        currentByte = int(currentBits,2)
        byteArr.append(currentByte)

    file = open("output_encoder_lzss.bin","wb")
    file.write(byteArr)
    file.close()
    ftext.close()