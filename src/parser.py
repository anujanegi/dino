FUNCTIONS = ['matmul', 'matvec', 'parsum']


def parse(filename):
    """ transform the file into a dino compatible file """
    final_code = """
    from mpi4py import MPI
    
    comm =  MPI.COMM_WORLD
    rank = MPI.Get_rank()
    size = MPI.Get_size()\n\n
    """
    with open(filename, 'r') as file:
        data = file.readline()
        for line in data:
            line = line.split('#')[0] # exclude pound comments
            for function in FUNCTIONS:
                if function+'(' in line:
                    # add function snippet to code
                    with open('../lib/'+function+'.py', 'r') as ffile:
                        final_code+=ffile.read()
                    final_code+="\n\n"
        final_code += """if rank == 0:\n"""
        for line in data:
            final_code += "\t" + line + "\n"
