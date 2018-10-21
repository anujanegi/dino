import os
import re

FUNCTIONS = ['matmul', 'matvec', 'parsum', 'hello']


def get_filename(old_name):
    dir_name = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(dir_name, old_name))


def parse(filename):
    """ transform the file into a dino compatible file """
    final_code = """
from mpi4py import MPI
import numpy as np
    
comm =  MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()\n\n
"""
    """
    top_block
    if rank == 0:
        top_if_block
    else:
        else_block
    global_block
    if rank == 0:
        bottom_if_block
    """
    top_block = []
    top_if_block = []
    else_block = []
    bottom_if_block = []
    global_block = []
    with open(filename, 'r') as file:
        data = file.readlines()
        for line in data:
            line = line.split('#')[0]   # exclude pound comments
            for func in FUNCTIONS:
                if func + '(' in line:
                    # add function snippet to code
                    with open(get_filename('../lib/'+func+'.py'), 'r') as ffile:
                        final_code += ffile.read()
                    final_code += "\n\n"
                    global_block.append(line)
                    match_obj = re.search(r'%s\((.+)\)' % func, line)
                    if match_obj:
                        params = match_obj.group(1).split(',')
                        for param in params:
                            else_block.append("%s = None\n" % param.strip())
                    continue
            if '=' in line:
                top_if_block.append(line)
                continue
            if 'import' in line:
                top_block.append(line)
                continue
            if line.strip():
                bottom_if_block.append(line)
        if top_block:
            for line in top_block:
                if "np" not in line:
                    final_code = line + "\n" + final_code
        if top_if_block:
            final_code += """if rank == 0:\n"""
            for line in top_if_block:
                if line not in global_block:
                    final_code += "\t" + line
        if else_block:
            final_code += """else:\n"""
            for line in else_block:
                final_code += "\t" + line
        if global_block:
            for line in global_block:
                final_code += line
        if bottom_if_block:
            final_code += """if rank == 0:\n"""
            for line in bottom_if_block:
                final_code += "\t" + line
    return final_code