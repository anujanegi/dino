def matmul(n, m, matrix1, x, y, matrix2):
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    n = comm.bcast(n, root=0)
    m = comm.bcast(m, root=0)
    x = comm.bcast(x, root=0)
    y = comm.bcast(y, root=0)

    if rank != 0:
        matrix1 = np.zeros(shape=(m, n))
        matrix2 = np.zeros(shape=(x, y))

    matrix1 = comm.bcast(matrix1, root=0)
    matrix2 = comm.bcast(matrix2, root=0)

    recvbuf = None
    if rank == 0:
        if size >= n:
            recvbuf = np.zeros(shape=(size,y), dtype='d')
        else:
            recvbuf = np.zeros(shape=(n + n%size,y), dtype='d')

    if n % size == 0:
        a = (n // size)
    else:
        a = (n // size) + 1

    partial_result = np.zeros(shape=(a,y), dtype='d')


    d = 0
    for i in range(rank, n, size):
        c = 0
        for j in range(m):
            for k in range(y):
                partial_result[d][c] += matrix1[i][k] * matrix2[k][j]
            c = c + 1
        d = d + 1

    print('rank',rank,'partial_result',partial_result)

    comm.barrier()
    comm.Gather(partial_result, recvbuf, root=0)

    if rank == 0:
        final = np.zeros(shape=(n*size,y), dtype='d')
        x = 0
        for i in range(0,size):
            for j in range(i,n,size):
                final[x] = recvbuf[j]
                x = x+1
                print('x',x)


        return final[0:n,0:y]
