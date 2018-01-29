#!/usr/bin/env python3
# Written by Alex Ding, 2018

import sys, os.path
import pyexcel as pe

# Note: need to install pyexcel and pyexcel-xls and pyexcel-xlsx
# https://github.com/pyexcel/pyexcel
# https://github.com/pyexcel/pyexcel-xls
# https://github.com/pyexcel/pyexcel-xlsx

PROGRAM_DESCRIPTION = """
Takes an output file name, a series of txt file 
 names, and a delimiter in command line argument 
 and convert each file into a sheet in the final 
 excel file
"""

USAGE_DESCRIPTION = """
Usage: python %s <output_name> <file1> [<file2>..<filen>] <delimiter>
Example: python %s output.xls foo1.txt foo2.txt "\\t"
Note: enclose delimiter by double quotes if it contains special
 characters or space
 output_name MUST be an excel file extension
 both .xls and .xlsx can be used
""" % (sys.argv[0], sys.argv[0])

def remove_extension(fname):
    """Returns the filename with extension stripped"""
    for i in range(len(fname)-1, 0, -1):
        if fname[i] == '.':
            return fname[0:i]

def print_and_exit(s):
    """Prints the string into stderr and exits"""
    print(s, file=sys.stderr)
    sys.exit()

def make_content(file_name, delimiter):
    """Return a 2D array representing the page"""
    content = []
    try:
        with open(file_name, "r") as f:
            for line in f:
                # strip away newline symbol
                newline_stripped = line
                if (line[-1] == "\n"):
                    newline_stripped = line[:-1]
                # append the array bt separating the line with the delimiter
                content.append(newline_stripped.split(delimiter))
    except IOError:
        print_and_exit("%s cannot be opened" % file_name)
    return content

def write_excel(inputs, output_name, delimiter):
    """Take a list of input file names and write to a file called output_name"""
    book_content = dict()
    # for each file, make a separate page
    for input_name in inputs:
        print("Reading from %s" % input_name)
        book_content[remove_extension(input_name)] = make_content(input_name, delimiter)

    # create book object and save the file
    try:
        book = pe.Book(book_content)
        book.save_as(output_name)
    except:
        print_and_exit("Cannot create EXCEL file! Invalid extension in %s" % output_name)

# check minimum arguments
if len(sys.argv) < 4:
    print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)

# read user inputs
delimiter = bytes(sys.argv[-1], "utf-8").decode("unicode_escape")
output_name = sys.argv[1]
input_names = sys.argv[2:-1]

write_excel(input_names, output_name, delimiter)
