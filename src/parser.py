import os
import re

FUNCTIONS = ['matmul', 'matvec', 'parsum']


def get_filename(old_name):
    dir_name = os.path.dirname(__file__)
    return os.path.join(dir_name, old_name)


def parse(filename):
    """ transform the file into a dino compatible file """
    final_code = """
from mpi4py import MPI
    
comm =  MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()\n\n
"""
    else_block = []
    global_block = []
    with open(filename, 'r') as file:
        data = file.readlines()
        for line in data:
            line = line.split('#')[0]   # exclude pound comments
            for function in FUNCTIONS:
                if function+'(' in line:
                    # add function snippet to code
                    with open(get_filename('../lib/'+function+'.py'), 'r') as ffile:
                        final_code+=ffile.read()
                    final_code+="\n\n"
                    global_block.append(line)
                    match_obj = re.search(r'\((.*)\)', line)
                    if match_obj:
                        params = match_obj.group(1).split(',')
                        for param in params:
                            else_block.append("%s = None" % param)
        final_code += """if rank == 0:\n"""
        for line in data:
            if line not in global_block:
                final_code += "\t" + line
        if else_block:
            final_code += """else:\n"""
            for line in else_block:
                final_code += "\t" + line + "\n"
        for line in global_block:
            final_code += line + "\n"

    return final_code