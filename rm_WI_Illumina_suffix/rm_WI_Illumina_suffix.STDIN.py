#!/usr/bin/env python3
# Written by Alex Ding, 2018

import sys

PROGRAM_DESCRIPTION = """
Remove special suffix appearing in WI Illumina fastq files
 by changing /1;0 and /2;0 in the read description
 (lines begin with @ and +) to /1 and /2
"""

USAGE_DESCRIPTION = "\nUSAGE: python %s < foo.fastq > foo_noSuffix.fastq\n" % sys.argv[0]

def print_and_exit(s):
    """prints the error message and exits"""
    print(s, file=sys.stderr)
    sys.exit()


# note that the file has read descriptions on all the odd lines
# they all start with "@" or "+" and end with "/1;0" and "/2;0"
# we change "/1;0" and "/2;0" into "/1" and "/2" and keep everything
# else the same
def parse_line(l):
    """parses one single line and prints it after revision"""
    # check validity of the line
    if l[0] == "@" or l[0] == "+":
        # print everything prior to the end bit (which is /1;0 or /2;0)
        # [:-5] -> everything prior to the last 4 characters
        print(l[:-5], end="")
        # check which one it is and print accordingly
        if l[-4] == "1":
            print("/1")
        elif l[-4] == "2":
            print("/2")
        else:
            print_and_exit("File not complying to format")
    else:
        print_and_exit("File not complying to format")

count = 0

# check if stdin is empty
if sys.stdin.isatty():
    print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)
else:
    for line in sys.stdin:
        # if it's line 1, 3, 5...
        if count % 2 == 0:
            # process it
            parse_line(line)
        else:
            # just print the original line
            print(line, end="")
        count = count + 1

if count == 0:
    print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)