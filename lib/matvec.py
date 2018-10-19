def matvec( n, m, matrix, vector):
    n = comm.bcast(n, root=0)
    m = comm.bcast(m, root=0)

    if rank != 0:
        matrix = np.zeros(shape=(m, n))
        vector = np.zeros(n)

    matrix = comm.bcast(matrix, root=0)
    vector = comm.bcast(vector, root=0)
    recvbuf = None

    if rank == 0:
        if size >= n:
            recvbuf = np.zeros(size, dtype='d')
        else:
            recvbuf = np.zeros(n + n%size, dtype='d')

    if n % size == 0:
        a = (n // size)
    else:
        a = (n // size) + 1
    partial_result = np.zeros(a, dtype='d')

    k = 0
    for i in range(rank, n, size):
        for j in range(m):
            partial_result[k] += matrix[i][j] * vector[j]
        k = k+1

    comm.barrier()
    comm.Gather(partial_result, recvbuf, root=0)

    if rank == 0:    
        final = []
        for i in range(0, size):
            for j in range(i,len(recvbuf),size):
                y = recvbuf[j]
                final.append(y)

        return final[:n]
