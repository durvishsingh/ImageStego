from PIL import Image
import sys


class LSB():
    def __init__(self, filename):
        self.filename = filename
        self.message = None
        self.cover = None
        self.bits = None

    def open_image(self):
        try:
            self.cover = Image.open(self.filename)
            return True
        except FileNotFoundError as e:
            print('Error: ' + self.filename + ' does not exist. Please specify an existing file')
            return False

    def get_bit_depth(self):
        # 1 (1-bit pixels, black and white, stored with one pixel per byte)
        # L (8-bit pixels, black and white)
        # P (8-bit pixels, mapped to any other mode using a color palette)
        # RGB (3x8-bit pixels, true color)
        # RGBA (4x8-bit pixels, true color with transparency mask)
        # CMYK (4x8-bit pixels, color separation)
        # YCbCr (3x8-bit pixels, color video format)
        # Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
        # LAB (3x8-bit pixels, the L*a*b color space)
        # HSV (3x8-bit pixels, Hue, Saturation, Value color space)
        # I (32-bit signed integer pixels)
        # F (32-bit floating point pixels)
        mode_to_bd = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}

        if self.cover is not None:
            return mode_to_bd[self.cover.mode]


    def messageToBits(self, string):
        bits = []
        
        # Convert each character into binary and pad with 0s
        for char in string:
            binval = bin(ord(char))[2:].rjust(8,'0')
            
            #for bit in binval: 
            bits.append(binval)

        return bits

    """ Validates that the message can fit into the specified file
        Counts the number of bits in the secret message and 
        compares it to how much space exists in the cover image """
    def validate(self):
        img = self.open_image()
        
        # Find the capacity of the image
        capacity = 0
        if img:
            capacity = self.cover.width * self.cover.height * (self.get_bit_depth()/8)
            # print ('Capacity of image:\t' + str(capacity))

        # Convert the string message into bits 
        self.bits = ''.join(self.messageToBits(self.message))
        #print('Message bits:\t\t' + str(len(self.bits)))


        if len(self.bits) >= capacity:
            print('Error: The message is too long to be encoded into the image ' + self.filename)
            return False

        return True


    def setComponentLSB(self,component, bit):
        # 5 = 0000 0101
        # bit = 0
        # 1 = 0000 0001
        # ~1 = 1111 1110
        # 0000 0101
        # 1111 1110
        # 0000 0100
        # 0000 0000

        blankLSB = component & ~1
        return blankLSB | int(bit)


    def hide(self, secretMessage, outFilename):
        # Add length of message to message
        self.message = str(len(secretMessage)) + ':' + secretMessage

        # Check that the message can fit inside the image
        if not self.validate():
            print ('Error: Validation failed. Cannot encode message into image')
            return

        # Image.copy()
        # Copies this image. Use this method if you wish to paste things into an image, but still retain the original.

        # Return type:    Image
        # Returns:    An Image object.

        encodedImage = self.cover.copy()

        # PIL.Image.size
        # Image size, in pixels. The size is given as a 2-tuple (width, height).

        # Type:   (width, height)

        width, height = self.cover.size

        # Position within bits of message
        index = 0

        for row in range(height):
            for col in range(width):

                if index + 1 <= len(self.bits):

                    (r,g,b) = encodedImage.getpixel((col, row))

                    r = self.setComponentLSB(r, self.bits[index])

                    if index + 2 <= len(self.bits):
                        g = self.setComponentLSB(g, self.bits[index+1])
                    
                    if index + 3 <= len(self.bits):
                        b = self.setComponentLSB(b, self.bits[index+2])

                    # Set new pixel values
                    encodedImage.putpixel((col,row),(r,g,b))

                index += 3

        encodedImage.save(outFilename)

        return encodedImage


    def extract(self):
        img = self.open_image()
        width, height = self.cover.size

        buff = 0
        count = 0

        messageBits = []
        msgSize = None

        for row in range(height):
            for col in range(width):
                # 17:Durvish and Utsav
                # Go through each RGB component and pull uot the LSB
                for component in self.cover.getpixel((col, row)):
                    # Read the bit and push left to make 8 bit chunk
                    buff += (component & 1) << (7 - count)
                    count += 1

                    # Convert 8 bit chunk to char and append 
                    if count == 8:
                        messageBits.append(chr(buff))
                        buff = 0    # Reset buffer
                        count = 0   # and count

                        # If we read the separator last, set the message size
                        if messageBits[-1] == ':' and msgSize is None:
                            try:
                                msgSize = int(''.join(messageBits[:-1]))
                            except:
                                pass

                # Return the message when bits read match size of message
                if len(messageBits) - len(str(msgSize)) - 1 == msgSize:
                    return ''.join(messageBits)[len(str(msgSize))+1:]

        return ''
