def my_first_prog():
    name = MPI.Get_processor_name()
    print("hello i m rank:", rank, "from processor:", name)
