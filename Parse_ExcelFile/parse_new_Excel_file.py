#!/usr/bin/env python3
# Written by Alex Ding, 2018

import sys, os.path
import pyexcel as pe

PROGRAM_DESCRIPTION = """
Takes an excel file name and an optional delimiter
 (default is tab) in command line argument and
 convert each sheet into a txtfile
"""
USAGE_DESCRIPTION = """
Usage: python %s <file_name> [delimiter="\\t"]
Example: python %s foo.xls ","
Note: both .xls and .xlsx can be used
""" % (sys.argv[0], sys.argv[0])

def print_and_exit(message):
    print(message, file=sys.stderr)
    exit()

def remove_extension(fname):
    """Return the filename with extension stripped"""
    for i in range(len(fname)-1, 0, -1):
        if fname[i] == '.':
            return fname[0:i]

def write_txt(sheet, d, fname):
    """Export the sheet into a tab-separated txt file"""
    f = open(sheet.name + "_" + fname + ".txt", "w")
    i = 1
    for row in sheet:
        j = 1
        for value in row:
            f.write(str(value))
            # write delimiter unless it's the end
            if j != len(row):
                f.write(d)
            j = j+1
        # write newline unless it's the end
        if i != sheet.number_of_rows():
            f.write("\n")
        i = i+1
    f.close()
    

def read_excel_file(fname, d):
    """Read an entire excel file and output each sheet as a txt file"""
    try:
        book = pe.get_book(file_name=fname)
    except pe.exceptions.FileTypeNotSupported:
        print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+
                       "\nInput file must be of excel extension!\n")
    except:
        print_and_exit("\nInput file corrupt!\n")
    for name in book.sheet_names():
        print("Printing sheet %s" % name)
        write_txt(book.sheet_by_name(name), d, remove_extension(fname))
        

# check if filename given
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)
    sys.exit()

delimiter = "\t"
if len(sys.argv) == 3:
    delimiter = bytes(sys.argv[2], "utf-8").decode("unicode_escape")

# check if file exists
if not os.path.isfile(sys.argv[1]):
    print_and_exit("%s does not exist" % sys.argv[1])

print("Reading %s" % sys.argv[1])
read_excel_file(sys.argv[1], delimiter)
print("Success!")
