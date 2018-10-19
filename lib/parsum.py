def parsum(t, data):
    t = comm.bcast(t, root=0)
    data = comm.bcast(data, root=0)

    if(t%size == 0):
        recvbuf = np.empty(t // size, dtype='d')  # allocate space for recvbuf
        comm.Scatter(data, recvbuf, root=0)

        partial_sum = 0

        for x in range(len(recvbuf)):
            partial_sum += recvbuf[x]

        # print(partial_sum)
        value = np.array(partial_sum, 'd')

        sum = np.array(0.0, 'd')
        comm.Reduce(value, sum, op=MPI.SUM, root=0)

        if rank == 0:
            return sum

    else:
        a=t%size

        if rank ==0:
            recvbuf = np.empty((t // size), dtype='d')  # allocate space for recvbuf
            extra = []

            for i in range(1, a+1):
                a = data[-1]
                extra.append(a)
                z = len(data) - 1
                data = np.delete(data, z)
        else:
            recvbuf = np.empty((t // size), dtype='d')  # allocate space for recvbuf


        data = comm.bcast(data, root=0)

        comm.Scatter(data, recvbuf, root=0)

        partial_sum = 0

        for x in range(len(recvbuf)):
            partial_sum += recvbuf[x]

        if rank == 0:
            for x in extra:
                partial_sum += x

        value = np.array(partial_sum, 'd')

        sum = np.array(0.0, 'd')
        comm.Reduce(value, sum, op=MPI.SUM, root=0)

        if rank == 0:
            return sum
