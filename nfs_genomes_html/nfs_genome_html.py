#!/usr/bin/env python3
# Written by Alex Ding, 2018

import os, sys
import pyexcel as pe

# Note: need to install pyexcel and pyexcel-xls and pyexcel-xlsx
# https://github.com/pyexcel/pyexcel
# https://github.com/pyexcel/pyexcel-xls
# https://github.com/pyexcel/pyexcel-xlsx

PROGRAM_DESCRIPTION = """
Generates an HTML page or EXCEL file outlining 
 a table providing information about whether or
 not certain genetic datum of a species is present
"""
USAGE_DESCRIPTION = """
Usage: %s <directory> <output_filename>
Example: %s /nfs/genomes/ BaRC_genomes
Note: omit extension in output_filename
""" % (sys.argv[0], sys.argv[0])
HEADER_FILE_NAME = "header.html"
TABLE_FILE_NAME = "table.html"
FOOTER_FILE_NAME = "footer.html"


def row_td(info, color=None):
    """makes a td tag out of the text inside"""
    return "<td>%s</td>\n" % info if color is None else """<td class="%s">%s</td>\n""" % (color, info)

def bool_none_handle(bool_none):
    """takes a bool/None an return the appropriate text"""
    if bool_none is None:
        return ""
    elif bool_none:
        return "Yes"
    return "No"

class GenomeInfo:
    """stores the genome availability info for a certain strain"""
    # could rewrite these variables to be read from a json file
    folder_names = ["anno", "bed", "blast", "blat", "bowtie", "bwa", "fasta", 
                    "fasta_whole_genome", "gff", "gtf", "hisat", "igv", "liftOver", "maf", "rsem",
                    "snp", "STAR", "10x"]
    to_skip = ["seq", ".etc", "mouse_gp_mar_06", "lost+found", "custom",
               ".snapshot", "NGS_adapters_primers", "rRNAs", "TO_DELETE"]
    to_go_down = ["S_cerevisiae_strains", "rRNAs"]
    alias_file_name = "GENOME_ALIASES"

    def __init__(self, folder):
        self.folders_presence = {}
        for folder_name in self.folder_names:
            self.folders_presence[folder_name] = False
        self.assembly_aliases = []
        self.scientific_name = "N/A"
        self.common_name = "N/A"
        self.folder_name = folder

    def populate(self, directory):
        """fills in the variables appropriately"""
        folders = next(os.walk(directory))[1]
        # handles the folder_presence dict correctly
        for folder in folders:
            # if folder is one of the things we look for
            # and if folder is non-empty
            if folder in self.folder_names and os.listdir(directory+"/"+folder):
                self.folders_presence[folder] = True

        # deals with the aliases/names
        if os.path.exists(directory+"/"+self.alias_file_name):
            alias = open(directory+"/"+self.alias_file_name)
            self.scientific_name = alias.readline()[:-1]
            self.common_name = alias.readline()[:-1]
            for line in alias:
                self.assembly_aliases.append(line[:-1])
            alias.close()

    def row(self):
        """generates HTML row based on the current info"""
        content = row_td("<b>" + self.scientific_name + "</b>") + row_td(self.common_name) + row_td(self.folder_name)
        content = content + row_td("N/A") if len(self.assembly_aliases) == 0 else content + row_td(", ".join(self.assembly_aliases))

        for file_ in self.folder_names:
            content = content + row_td(bool_none_handle(self.folders_presence[file_]))
        return "<tr>" + content + "</tr>"

def print_and_exit(message):
    """prints the error message and exits the program"""
    print(message, file=sys.stderr)
    exit()

def generate_gene_info(directory, folder_name):
    """takes a directory to a subfolder and generates html row"""
    gen = GenomeInfo(folder_name)
    gen.populate(directory+"/"+folder_name)
    return gen

def write_html_file(html_file_name, directory):
    """takes a file name and write everything as needed"""
    html_file = open(html_file_name, "w")

    # write the header
    with open(HEADER_FILE_NAME, "r") as header:
        content = header.read()
        html_file.write(content)
    # fill in the file name for the corresponding excel file
    html_file.write(html_file_name[:-5]+".xls")

    # write the head of the table
    with open(TABLE_FILE_NAME, "r") as table:
        content = table.read()
        html_file.write(content)

    # fill in custom data into the table
    if not os.path.exists(directory):
        print_and_exit("%s does not exist or cannot be accessed" % directory)
    files = next(os.walk(directory))[1]
    gens = []
    for file_ in files:
        if file_ in GenomeInfo.to_go_down:
            subfiles = next(os.walk(directory+"/"+file_))[1]
            for subfile_ in subfiles:
                gens.append(generate_gene_info(directory, file_+"/"+subfile_))
        elif file_ not in GenomeInfo.to_skip:
            gens.append(generate_gene_info(directory, file_))

    # loop through the resulting list to append properly to the HTML
    for gen in sorted(gens, key=lambda x: x.scientific_name):
        html_file.write(gen.row())
    # write the footer
    with open(FOOTER_FILE_NAME, "r") as footer:
        content = footer.read()
        html_file.write(content)

    html_file.close()

def insert_dict(content, gen):
    """insert the information of one entry into the dictionary"""

    content["Scientific Name"].append(gen.scientific_name)
    content["Common Name"].append(gen.common_name)
    content["Directory"].append(gen.folder_name)
    if len(gen.assembly_aliases) == 0:
        content["Assembly Alias(es)"].append("N/A")
    else:
        content["Assembly Alias(es)"].append(", ".join(gen.assembly_aliases))
    for folder in GenomeInfo.folder_names:
        content[folder].append(bool_none_handle(gen.folders_presence[folder]))

def dict_to_array(content):
    """takes a dict of 1D lists and converts into 2D list"""
    length = len(content["Scientific Name"])
    names = ["Scientific Name", "Common Name", "Directory",
             "Assembly Alias(es)"] + GenomeInfo.folder_names
    result = [names]
    for _ in range(0, length):
        result.append([])
    for name in names:
        for i in range(1, length+1):
            result[i].append(content[name][i-1])
    return result

def write_excel_file(output_filename, directory):
    """takes a file name, creates the EXCEL file, and writes as needed"""
    # initialize dict
    content = dict()
    content["Scientific Name"] = []
    content["Common Name"] = []
    content["Directory"] = []
    content["Assembly Alias(es)"] = []
    for name in GenomeInfo.folder_names:
        content[name] = []
    if not os.path.exists(directory):
        print_and_exit("%s does not exist or cannot be accessed" % directory)
    files = next(os.walk(directory))[1]
    gens = []
    
    for file_ in files:
        if file_ in GenomeInfo.to_go_down:
            subfiles = next(os.walk(directory+"/"+file_))[1]
            for subfile_ in subfiles:
                gen = GenomeInfo(file_+"/"+subfile_)
                gen.populate(directory+"/"+file_+"/"+subfile_)
                gens.append(gen)
        elif file_ not in GenomeInfo.to_skip:
                gen = GenomeInfo(file_)
                gen.populate(directory+"/"+file_)
                gens.append(gen)
    for gen in sorted(gens, key=lambda g:g.scientific_name):
        insert_dict(content, gen)
    sheet = pe.Sheet(dict_to_array(content))
    sheet.save_as(output_filename)

def depatchBothExtensions(output_filename, directory):
    """determines the extension and dispatches to correct function"""
    write_html_file(output_filename+".html", directory)
    write_excel_file(output_filename+".xls", directory)

if len(sys.argv) != 3:
    print_and_exit(PROGRAM_DESCRIPTION+USAGE_DESCRIPTION)

depatchBothExtensions(sys.argv[2], sys.argv[1])
