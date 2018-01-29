./groupBy.py -i sample_input.txt -g 1,2 -c 8-10,12,13-15,16 -o mean,collapse,median,mean > sample_output.txt
./groupBy_header.py -i sample_input.txt -g 1,2 -c 8-10,12,13-15,16 -o mean,collapse,median,mean > sample_output.txt

# the header version is used to handle the current bug in groupBy that gives all
# the original headers when -header is used, instead of using only headers from the
# columns we're asking for
# the header version assumes that the user wants header and hence automatically
# adds the -header flag. It then parses the output to give out only the headers
# of the columns the user specified