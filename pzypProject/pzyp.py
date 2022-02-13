"""
Main logic:
    1. Operation through command line with use of arguments
    2. Choice of input file for compression or decompression
    3. Alterations through compressor(+ textChar_elements) or decompressor functions
    4. Creation of output file with appropriate file extension

Compressor (+ textChar_elements) logic:
    1.Usage of information in input file
    2.FOR LOOP:
        1.index obtained through textChar_elements

Decompressor logic:
    1.Usage of information in input file
"""

import sys
from collections import deque #double-ended queue

def textChar_elements(textChar_verify2, buffer2):

    textChar_count = 0
    distance = 0

    for element in buffer2:
        
        if len(textChar_verify2) <= distance:
            return textChar_count - len(textChar_verify2)

        if textChar_verify2[distance] == element:
            distance += 1
        else:
            distance = 0

        textChar_count += 1

    return -1

def compressor(text_input, window=4096):

    buffer = deque(maxlen = window)
    textChar_verify = []
    output = []
    i = 0

    for char in text_input:
        index = textChar_elements(textChar_verify, buffer)

        if textChar_elements(textChar_verify + [char], buffer) == -1 or i == len(text_input) - 1:

            if i == len(text_input) - 1 and textChar_elements(textChar_verify + [char], buffer) != -1:
                textChar_verify.append(char)

            if len(textChar_verify) > 1:
                index = textChar_elements(textChar_verify, buffer)
                distance = i - index - len(textChar_verify)
                length = len(textChar_verify)

                coordenates = f"<{distance},{length}>"

                if len(coordenates) > length:
                    output.extend(textChar_verify)
                else:
                    output.extend(coordenates)

                buffer.extend(textChar_verify)

            else:
                output.extend(textChar_verify)
                buffer.extend(textChar_verify)

            textChar_verify = []

        if char == "<":
            textChar_verify.append(char)
            textChar_verify.append(char)

        if char != "<":
            textChar_verify.append(char)

        textChar_verify.append(char)

        if len(buffer) > window:
            buffer.popleft()

        i += 1
    
    text_output = "".join([str(int) for int in output])
    return (text_output)

def decompressor(text_input):
    
    output = []

    coordenates = False
    distance_verify = True

    distance = []
    length = []

    for char in text_input:
        if char == "<":
            coordenates = True
            distance_verify = True

        elif char == ",":
            distance_verify = False

        elif char == ">" and coordenates:
            coordenates = False

            try:
                length_int = int("".join([str(int) for int in length]))
                distance_int = int("".join([str(int) for int in distance]))

                actualText = output[-distance_int:][:length_int]

                output.extend(actualText)

            except Exception:
                print("PzypError: Invalid coordenates")

            length = []
            distance = []

        elif coordenates:
            if distance_verify == True:
                distance.append(char)
            else:
                length.append(char)

        else:
            output.append(char)

    text_output = "".join([str(int) for int in output])
    return (text_output)

def main():

    if len(sys.argv) > 3:

        print(f"User Manual: python[3] {sys.argv[0]} FILE_NAME.TXT OR -d FILE_NAME.LZS")
        sys.exit(2)

    elif len(sys.argv) == 2:

        input_file = sys.argv[1]

        file = open(input_file,'r')
        read_file = file.read()
        file.close()

        with open('compressed.lzs', 'w') as output:
            comp_file = compressor(read_file)
            output.write(comp_file)

    elif len(sys.argv) == 3:

        if sys.argv[1] == "-d":

            input_file = sys.argv[2]

            file = open(input_file,'r')
            read_file = file.read()
            file.close()

            with open('decompressed.txt', 'w') as output:
                decomp_file = decompressor(read_file)
                output.write(decomp_file)
        
        else:
            print(f"User Manual: python[3] {sys.argv[0]} -d FILE_NAME.LZS")
            sys.exit(2)

if __name__ == '__main__':
    sys.exit(main())

