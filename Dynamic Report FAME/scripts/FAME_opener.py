

import argparse
import numpy as np

# Define the argparser
parser = argparse.ArgumentParser(
        prog = "FAME Crasher",
        usage = "FAME_opener.py -f path/to/file/file.csv -o path/to/file/processed.csv \n"+ "V.0\n",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-f", help = "Introduce the ubication of the file and the file to process") # with a default parameter inside the function the program can run without comand line. ej. default = "path/to/file"
parser.add_argument("-o", help = "Desired name for the file")

# Extract the arguments

args = parser.parse_args()


# Parse the file to process
print(f'The file {args.f} is going to be process')

file = open(args.f,"r")
for line, content_line in enumerate(file):
    content = content_line.replace("\n", "")
    # Save the compounds name in the first row
    if line == 0:
        list_content = content.split(",")
        
        # Remove posible blank cells from the file and the first position wich have no metabolite information
        list_content.pop(0)
        metabolite_list = new_list = list(filter(None, list_content))
        file_list = list()
    
    # On the second row there are the Col names and the structure of the final file.
    elif line == 1:
        blank_counts = 0
        list_content = content.split(",")
        stop = True
        for element in list_content:
            if len(element) == 0 and stop:
                blank_counts += 1
            else:
                stop = False
        
        start = list_content.index("Area")
        list_2_label = list_content[start:]
        new_list = list()

        if list_content.count("RT") != 0:
            for e, metabolite_label in enumerate(metabolite_list):
                new_list.append(metabolite_label+"_"+list_2_label[e*2])
                new_list.append(metabolite_label+"_"+list_2_label[(e*2)+1])
        else:
            new_list = [e+i for e,i in zip(metabolite_list, list_2_label)] 

        append_list = list_content[blank_counts:start]+new_list
        file_list.append(append_list)
        
    else:
        file_list.append(content.split(",")[blank_counts:])
    
        

    if line>1 and len(file_list[0])!=len(list_content[blank_counts:]):
        print(f'In line {line} the lenght of the data({len(list_content[blank_counts:])}) and the number of columns{len(file_list[0])} is not the same')
        

# Save the file

np.savetxt(args.o, file_list, delimiter=",", fmt='%s')
