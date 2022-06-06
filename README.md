# ImageStego
Inline Arguments : 

stego.py [-h] [-d] [-a] -i FILE [-o FILE] [-s STRING] [-f FILE]

-d 
Set method to decode, default is encode

-a
Set encoding/decoding algorithm to LSB, default is DCT

-i
Specify input file name

-o 
Output file name (optional)

-s 
Message string to encrypt

-f 
Message text file to encrypt

Example : 
1. Encrypt "GitHub is cool" into the input image {path}/lenna.png into output image {path}/lenna_02.png using LSB (Least Significant Bit) method.

Command : python stego.py -a -i lenna.png -o lenna_02.png -s "GitHub is cool"

2. Retrieve hidden message from {path}/lenna_02.png via LSB (Least Significant Bit) method.

Command : python stego.py -d -a -i lenna_02.png