import os

FUNCTIONS = ['matmul', 'matvec', 'parsum']


def get_filename(old_name):
    dir_name = os.path.dirname(__file__)
    return os.path.join(dir_name, old_name)


def parse(filename):
    """ transform the file into a dino compatible file """
    final_code = """
from mpi4py import MPI
    
comm =  MPI.COMM_WORLD
rank = MPI.Get_rank()
size = MPI.Get_size()\n\n
"""
    with open(filename, 'r') as file:
        data = file.readlines()
        for line in data:
            line = line.split('#')[0] # exclude pound comments
            for function in FUNCTIONS:
                if function+'(' in line:
                    # add function snippet to code
                    with open(get_filename('../lib/'+function+'.py'), 'r') as ffile:
                        final_code+=ffile.read()
                    final_code+="\n\n"
        final_code += """if rank == 0:\n"""
        for line in data:
            final_code += "\t" + line
    return final_code