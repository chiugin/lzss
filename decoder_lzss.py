# FIT3155 Assignment 3 Task 2 decoder
# Name: Chong Chiu Gin
# Student ID: 28842022

import sys

class Node:
    """
    Class representing tree node
    """
    def __init__(self, value, left, right):
        self.value = value # the char at the leaf
        self.left = left
        self.right = right


class PreOrderIterator:
    """
    iterator for bitstring
    Implementation from lecture 31 of FIT1008
    """
    def __init__(self, current):
        self.stack = []
        self.stack.append(current)

    def __iter__(self):
        return self

    def __next__(self):
        if self.stack == []:
            raise StopIteration
        current = self.stack.pop()
        if current.right is not None:
            self.stack.append(current.right)
        if current.left is not None:
            self.stack.append(current.left)
        return current.value

class HuffmanBinaryTree:
    """
    class representing binary tree for huffman
    Implementation of this tree is based on Lecture 31 of FIT1008
    """

    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def __iter__(self):
        return PreOrderIterator(self.root)

    def __len__(self):
        return self._len_aux(self.root)

    def _len_aux(self, current):
        if current is None:
            return 0
        else:
            return 1 + self._len_aux(current.left) + self._len_aux(current.right)

    def add(self, value, bitstring_instruction):
        bit_iter = iter(bitstring_instruction)
        self.root = self.add_aux(self.root, value, bit_iter)

    def add_aux(self, current, value, bit_iter):
        if current is None:
            current = Node(None, None, None)

        try:
            bit = next(bit_iter)
            if bit == '0':
                current.left = self.add_aux(current.left, value, bit_iter)
            elif bit == '1':
                current.right = self.add_aux(current.right, value, bit_iter)
        except StopIteration:
            current.value = value
        return current

    def search(self,bitstring, pointer):
        return self.search_aux(self.root,bitstring,pointer)

    def search_aux(self,current, bitstring, pointer):
        if current is not None:
            if current.value is not None:
                return current.value,pointer
            else: #not a leaves
                if bitstring[pointer] == '0':
                    return self.search_aux(current.left, bitstring, pointer+1)
                elif bitstring[pointer] == '1':
                    return self.search_aux(current.right, bitstring,pointer+1)
        return "decoding error"

    def print_preorder(self):
        self.print_preorder_aux(self.root)

    def print_preorder_aux(self, current):
        if current is not None:
            print(current.value)
            self.print_preorder_aux(current.left)
            self.print_preorder_aux(current.right)

    def print_inorder(self):
        self.print_inorder_aux(self.root)

    def print_inorder_aux(self, current):
        if current is not None:
            self.print_inorder_aux(current.left)
            print(current.value)
            self.print_inorder_aux(current.right)

    def collect_leaves(self):
        list_leaves = []
        self._collect_leaves_aux(self.root, list_leaves)
        return list_leaves

    def _collect_leaves_aux(self, current, list_leaves):
        if current is not None:
            if self.isLeaves(current):
                list_leaves.append(current.value)
            else:
                self._collect_leaves_aux(current.left, list_leaves)
                self._collect_leaves_aux(current.right, list_leaves)

    def isLeaves(self, current):
        return current.left is None and current.right is None


def elias_decode(string,pointer):
    """
    decoding elias to get the integer value
    :param string: the plaintext to be decoded
    :param pointer: starting position of current bitstring to be decoded
    :return: decoded integer and the next pointer
    """

    # if pointer points at '1', then return 1
    if string[pointer] == '1':
        return 1, pointer+1

    currIndex = pointer
    length = 1
    while string[currIndex] != '1':
        elias_text = '1' + string[currIndex+1:currIndex+length]
        currIndex += length
        decodedInteger = binary2decimal(elias_text)
        length = decodedInteger+1

    elias_text = string[currIndex:currIndex+length]
    decodedInteger = binary2decimal(elias_text)

    #return decodedInteger (type int) AND start position of rest of the string
    return decodedInteger, currIndex + length

def binary2decimal(text):
    """
    converts binary to decimal
    :param text: the binary text
    :return: the decimal integer value
    """
    return int(text,2)

def lzss_decode(string):
    """
    the main code to be decoded
    :param string: plaintext to be decoded
    :return: the decoded text
    """

    huffmanCodesTable = [None for x in range(128)]

    # decoding header
    uniqueCharNum, pointer = elias_decode(string, 0)
    # for every unique char
    for i in range(uniqueCharNum):

        #1. decode the ASCII char - first 7 bits
        asciiBitString = string[pointer:pointer+7]
        asciiNumber = binary2decimal(asciiBitString)
        asciiChar = chr(asciiNumber)

        #2. elias decode to get the length of this char's huffman code
        pointer += 7
        huffmanCodeLength, pointer = elias_decode(string, pointer)

        #3. get the huffman code for this char based on length found in step (2)
        huffmanCode = string[pointer:pointer+huffmanCodeLength]

        #save the huffman code of this ascii char in the huffman code table
        huffmanCodesTable[ord(asciiChar)] = huffmanCode

        # set pointer for next char
        pointer += huffmanCodeLength

    #build huffman tree to decode info part
    huffmanTree = HuffmanBinaryTree()
    #add into huffmanTree
    for i in range(len(huffmanCodesTable)):
        if huffmanCodesTable[i] is not None:
            huffmanTree.add(chr(i),huffmanCodesTable[i])

    #decoding info
    #elias decode to get number of format fields
    formatNum , pointer = elias_decode(string,pointer)

    # get values of each format fields
    formatFields = []
    for i in range(formatNum):
        if string[pointer] == '1':
            pointer += 1
            # search in binary tree until it reaches leaf to get the char!
            char, pointer = huffmanTree.search(string,pointer)
            formatFields.append([1,char])
        elif string[pointer] == '0':
            pointer += 1
            offset, pointer = elias_decode(string,pointer)
            length, pointer = elias_decode(string,pointer)
            formatFields.append([0,offset,length])
        else:
            raise Exception("error in code")

    decodedText = ''
    #decode actual text using format fields
    for i in range(formatNum):
        formatField = formatFields[i]

        #if 1, then just get char and add to decodedText
        if formatField[0] == 1:
            decodedText += formatField[1]
        #if 0, need to decode text by copying matching text
        else:
            matchingStart = len(decodedText) - formatField[1]
            for i in range(formatField[2]):
                decodedText += decodedText[matchingStart]
                matchingStart += 1

    return decodedText


def decimal2binary(num):
    """
    convert num to binary string
    :param num: the decimal number
    :return: the binary string of num
    """
    numBin = bin(num)
    return numBin[2:]


if __name__ == "__main__":

    input_file = sys.argv[1]
    #input_file = "output_encoder_lzss.bin"

    ftext = open(input_file, "rb")
    text = ftext.read()

    plaintext = ""
    for i in range(len(text)):
        bitstring = decimal2binary(text[i])
        if len(bitstring)<8:
            bitstring = ('0'*(8-len(bitstring))) + bitstring
        plaintext += bitstring

    decodedText = lzss_decode(plaintext)

    with open("output_decoder_lzss.txt", "w") as fout:
        fout.write(decodedText)

    ftext.close()
    fout.close()

    oritext=''
    fori = open("input_apoorv.txt","r")
    #fori = open("input_sherwyn.txt", "r")
    for line in fori:
        oritext = line

    print(oritext == decodedText)


