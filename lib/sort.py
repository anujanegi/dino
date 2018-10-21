def merge(*args):
    left, right = args[0] if len(args) == 1 else args
    left_length, right_length = len(left), len(right)
    left_index, right_index = 0, 0
    merged = []
    while left_index < left_length and right_index < right_length:
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1
    if left_index == left_length:
        merged.extend(right[right_index:])
    else:
        merged.extend(left[left_index:])
    return merged

def merge_sort(data):
    length = len(data)
    if length <= 1:
        return data
    middle = length / 2
    left = merge_sort(data[:middle])
    right = merge_sort(data[middle:])
    return merge(left, right)


def sort(t, data):
    t = comm.bcast(t, root=0)
    data = comm.bcast(data, root=0)

    if(t%size == 0):
        recvbuf = np.empty(t // size, dtype='d')  # allocate space for recvbuf
        comm.Scatter(data, recvbuf, root=0)

        partial_sum = 0

        sorted_data = merge_sort(recvbuf)[

        if rank == 0:
            return sorted_data

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

        sorted_data = merge_sort(recvbuf)

        if rank == 0:
            return sorted_data
