#!/usr/bin/env python3
# Written by Alex Ding, 2018

import sys

PROGRAM_DESCRIPTION = """
This program takes in a bed-formatted file and a maximum number
 of BPs one wishes to go upstream to genes and calculates
 the maximum number of BPs one can go upstream without interfering with
 other genes. The strand_direction determine if we only consider strands
 going in the same direction or both directions. 
"""
USAGE_DESCRIPTION = """
Usage: %s <input_filename> <output_filename> <bp_limit> 
 <stream_direction> ("5", "3", or "both") [strand_direction=1 (1 or 2)]
Example: %s sample_input.bed sample_output.bed 2000 5
""" % (sys.argv[0], sys.argv[0])

def print_and_exit(message):
    """prints the error message and exits"""
    print(message, file=sys.stderr)
    exit()

def opposite(direction):
    """reverse direction"""
    if direction == "5":
        return "3"
    else:
        return "5"

def find_closest_two_direction(starts, ends, directions, bp_limit, from_id, gene_direction):
    """takes in two arrays of chromosome starts and ends and
    the index of the interested chromosome and it's direction
    returns the largest number of bases posible until another chromosome
    of any direction is reached"""
    if (directions[from_id] == "-" and gene_direction == "5") or (directions[from_id] == "+" and gene_direction == "3"):
        # loop through all the members
        for i in range(0, len(starts)):
            # ignore anything that ends before our node ends
            # and anything that goes in another direction
            if i != from_id and ends[i] > ends[from_id]:
                # if the segment starts before our segment ends and ends after our segment
                # it spans across the end of our segment and hence we can't write anything
                # to the end of our segment without overwriting this segment
                if starts[i] <= ends[from_id]:
                    return 0
                # compares existing min and distance between this segment with our segment
                # to find the closest start to our segment's end
                if starts[i] - ends[from_id] <= bp_limit:  
                    return starts[i] - ends[from_id]
                else:
                    return bp_limit
                # since starts are sorted, we can only get bigger starts from now on..
        return bp_limit
    # analogous case for forwards
    else:
        for i in range(from_id, 0, -1):
            if i != from_id and starts[i] < starts[from_id]:
                if ends[i] >= starts[from_id]:
                    return 0
                if starts[from_id] - ends[i] <= bp_limit:
                    return starts[from_id] - ends[i]
                else:
                    return bp_limit
        return bp_limit

def find_closest_one_direction(starts, ends, directions, bp_limit, from_id, gene_direction):
    """takes in two arrays of chromosome starts and ends and
    the index of the interested chromosome and it's direction
    returns the largest number of bases posible until another chromosome
    of the same direction is reached"""
    # handles the backward direction case
    if (directions[from_id] == "-" and gene_direction == "5") or (directions[from_id] == "+" and gene_direction == "3"):
        # loop through all the members
        for i in range(0, len(starts)):
            # ignore anything that ends before our node ends
            # and anything that goes in another direction
            if i != from_id and ends[i] > ends[from_id] and directions[i] != opposite(directions[from_id]):
                # if the segment starts before our segment ends and ends after our segment
                # it spans across the end of our segment and hence we can't write anything
                # to the end of our segment without overwriting this segment
                if starts[i] <= ends[from_id]:
                    return 0
                # compares existing min and distance between this segment with our segment
                # to find the closest start to our segment's end
                if starts[i] - ends[from_id] <= bp_limit:  
                    return starts[i] - ends[from_id]
                else:
                    return bp_limit
                # since starts are sorted, we can only get bigger starts from now on..
        return bp_limit
    # analogous case for forwards
    else:
        for i in range(from_id, 0, -1):
            if i != from_id and starts[i] < starts[from_id] and directions[i] != "-":
                if ends[i] >= starts[from_id]:
                    return 0
                if starts[from_id] - ends[i] <= bp_limit:
                    return starts[from_id] - ends[i]
                else:
                    return bp_limit
        return bp_limit

def write_output(output, chr, start, end, gene_name, direction, dist, gene_direction):
    output.write(chr+"\t")
    if (gene_direction == "5" and direction == "+") or (gene_direction == "3" and direction == "-"):
        # start and end are of the buffer
        # depends on the direction, get the right start and end
        output.write(str(start-dist)+"\t")
        output.write(str(start)+"\t")
    # analogous but reversed
    elif (gene_direction == "3" and direction=="+") or (gene_direction == "5" and direction == "-"):
        output.write(str(end)+"\t")
        output.write(str(end+dist)+"\t")
    # common tasks that both directions have to do
    output.write(gene_name+"_"+gene_direction+"_"+str(dist)+"\t")
    output.write("1\t")
    output.write(direction+"\n")

def write_outputs(output_filename, chrs, starts, ends, gene_names, directions, dists, gene_direction):
    """writes the output bed file from the accumulated info"""
    with open(output_filename, "w") as output:
        # go through each one and write the output
        for i in range(0, len(chrs)):
            # dispatch according to the direction(s) we go to
            if gene_direction == "both":
                write_output(output, chrs[i], starts[i], ends[i], gene_names[i], directions[i], dists[2*i], "5")
                write_output(output, chrs[i], starts[i], ends[i], gene_names[i], directions[i], dists[2*i+1], "3")
            elif gene_direction == "5":
                write_output(output, chrs[i], starts[i], ends[i], gene_names[i], directions[i], dists[i], "5")
            else:
                write_output(output, chrs[i], starts[i], ends[i], gene_names[i], directions[i], dists[i], "3")

def read_input_and_dispatch(input_filename, output_filename, bp_limit, gene_direction, direction):
    """read input from file and dispatches to the right algorithm"""
    chrs = []
    starts = []
    ends = []
    gene_names = []
    directions = []
    try:
        input_file = open(input_filename)
        # line by line and build up the initialized arrays
        for line in input_file:
            vals = line.split("\t") # get individual lines and read the different parts
            chrs.append(vals[0])
            starts.append(int(vals[1]))
            ends.append(int(vals[2]))
            gene_names.append(vals[3])
            directions.append(vals[5])
        input_file.close()
    except EnvironmentError: # if file cannot be opened
        print_and_exit("Invalid input file! Cannot open %s\n" % input_filename)
    except IndexError:
        print_and_exit("Incorrect file foramt! Check format for .bed files.\n"
                       + "Line Format: chrom start end name score direction ...")
   
    # sort inputs by starts
    result = sorted(zip(chrs, starts, ends, gene_names, directions), key=lambda tup:tup[1])
    # unpack the sorted input
    chrs = [x[0] for x in result]
    starts = [x[1] for x in result]
    ends = [x[2] for x in result]
    gene_names = [x[3] for x in result]
    directions = [x[4] for x in result]
    dists = [] # upstream distances - how much to go
    if direction == 1:
        for i in range(0, len(chrs)):
            if i+1 % 2000 == 0:
                print("%d done!" % i)
            if gene_direction == "both":
                dists.append(find_closest_one_direction(starts, ends, directions, bp_limit, i, "5"))
                dists.append(find_closest_one_direction(starts, ends, directions, bp_limit, i, "3"))
            else:
                dists.append(find_closest_one_direction(starts, ends, directions, bp_limit, i, gene_direction))
            
    else:
        for i in range(0, len(chrs)):
            if i+1 % 2000 == 0:
                print("%d done!" % i)
            if gene_direction == "both":
                dists.append(find_closest_two_direction(starts, ends, directions, bp_limit, i, "5"))
                dists.append(find_closest_two_direction(starts, ends, directions, bp_limit, i, "3"))
            else:
                dists.append(find_closest_two_direction(starts, ends, directions, bp_limit, i, gene_direction))
    write_outputs(output_filename, chrs, starts, ends, gene_names, directions, dists, gene_direction)

def check_parameters_and_dispatch():
    """check user inputs and supply the arguments properly"""
    # if incorrect number of parameters, quit
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)
    # if optional direction supplied, check if valid
    elif len(sys.argv) == 6:
        if int(sys.argv[5]) != 1 and int(sys.argv[5]) != 2:
            print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+"Direction must be 1 or 2\n")
        elif sys.argv[4] != "3" and sys.argv[4] != "5" and sys.argv[4] != "both":
            print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+"Stream direction must be 5 or 3 or both!\n")
        else:
            read_input_and_dispatch(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
    # if no optional direction, supply "1" as default
    else:
        if sys.argv[4] != "3" and sys.argv[4] != "5" and sys.argv[4] != "both":
            print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION+"Stream direction must be 5 or 3 or both!\n")
        else:
            read_input_and_dispatch(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], 1)

check_parameters_and_dispatch()
