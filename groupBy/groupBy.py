#!/usr/bin/env python3
# Written by Alex Ding, 2018

import sys
import subprocess
import datetime

PROGRAM_DESCRIPTION = """
This is a wrapper for groupBy. Takes the same flags
 but allows for range specification (with "-") in -c and 
 expands -c and -o arguments to follow groupBy's
 formatting E.g.: this converts -c 2-4,8 -o mean,collapse 
 into -c 2,3,4,8 -o mean,mean,mean,collapse
"""
USAGE_DESCRIPTION = """
Usage: see the following usage for groupBy and note that
 this wrapper supports range specifiers
Example: ./groupBy.py -i sample_input.txt -g 1 -c 8-10,12,13-15 -o mean,collapse,median
"""
LOG_FILENAME = "input_groupBy.log"

def print_and_exit(message):
    """prints the error message and exits"""
    print(message, file=sys.stderr)
    exit()

def call_and_exit(args, out=sys.stdout):
    """takes a list of arguments, calls groupBy, and returns the captured output"""
    try:
        # logs the actual command dispatched
        with open(LOG_FILENAME, "a") as log:
            log.write(datetime.datetime.now().strftime("%B %d, %Y: %I:%M%p") + "\n")
            log.write("./groupBy " + " ".join(args)+"\n")
            print("./groupBy " + " ".join(args)+"\n", file=sys.stderr)
    except IOError:
        print("Warning: log file non-existent", file=sys.stderr)
    subprocess.call(["groupBy"] + args, stdout=out)
    exit()

def parse_flags(cols, ops):
    """takes in two arrays and parse the columns to replace them accordingly"""

    # build up from empty strings
    cols_result = ""
    ops_result = ""
    
    # check if the numbers of flags match
    if (len(cols) > len(ops)):
        print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+
                       "\nNeed %d more -o flags to match the number of -c flags!\n" % (len(cols) - len(ops)))
    elif (len(cols) < len(ops)): 
        print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+
                       "\nNeed %d more -c flags to match the number of -o flags!\n" % (len(ops) - len(cols)))

    try:
        for ind, col in enumerate(cols):
            sep = col.find("-")
            # if col is in the form "1-3"
            if sep != -1:
                # expand the range specifiers
                for col_num in range(int(col[:sep]), int(col[sep+1:])+1):
                    cols_result = cols_result + str(col_num) + ","
                    ops_result = ops_result + ops[ind] + ","
            # else just simply append back
            else:
                cols_result = cols_result + col + ","
                ops_result = ops_result + ops[ind] + ","
    except (IndexError, ValueError):
        print_and_exit("\nIncorrect formatting! -c and -o must be " +
                       "lists of integers\n" + PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)
    # strips the last comma
    return (cols_result[:-1], ops_result[:-1])

def extend(args, col_id, ops_id):
    """replace columns and ops with extended flags"""
    args[col_id], args[ops_id] = parse_flags(args[col_id].split(","), args[ops_id].split(","))
    return args

columns_flag = None
operations_flag = None

for i, v in enumerate(sys.argv):
    # if end is reached without necessary flags supplied, call directly
    # this will forward groupBy's error message to stderr
    if v == "-c" or v == "-opCols":
        # check if no flag is supplied or if a flag immediately follows another
        if i+1 == len(sys.argv) or sys.argv[i+1].find("-") == 0:
            print(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION, file=sys.stderr)
            call_and_exit(sys.argv[1:], sys.stderr)
        columns_flag = i
    if v == "-o" or v == "-ops":
        # similar to the 1st case
        if i+1 == len(sys.argv) or sys.argv[i+1].find("-") == 0:
            print(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION, file=sys.stderr)
            call_and_exit(sys.argv[1:], sys.stderr)
        operations_flag = i

# if one of -o and -c is not found, quit
if operations_flag is None or columns_flag is None:
    print(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION, file=sys.stderr)
    if len(sys.argv) == 1:
        exit()
    call_and_exit(sys.argv[1:], sys.stderr)

# expand the range specifiers and call
call_and_exit(extend(sys.argv[1:], columns_flag, operations_flag))
