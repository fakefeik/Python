A program which helps you hide information in .bmp files. And recover information hidden in .bmp files.

Usage:
    bmp.py encode infile file_to_encode bits_count step [--outfile OUTFILE]
    bmp.py decode infile outfile bits_count step
    bmp.py search infile

encode infile file_to_encode bits_count step [--outfile OUTFILE]
    Encodes file_to_encode into infile and writes encoded information into OUTFILE.
    If OUTFILE is not specified, information will be written into infile.
    bits_count determines how many bits are replaced in a byte of bitmap image,
    step determines step with which bytes will be written.

decode infile outfile bits_count step
    Decodes information hidden in infile and writes decoded information into outfile.
    bits_count determines how many bits will be replaced in a byte of bitmap image,
    step determines step with which bytes will be read.

search infile bits_count step
    Searches infile for text or common file headers. If found, prints out text or 
    the file type, which header had been found. bits_count determines how many bits 
    will be replaced in a byte of bitmap image, step determines 
    step with which bytes will be read.

