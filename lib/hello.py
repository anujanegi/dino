def hello():
    name = MPI.Get_processor_name()
    print("hello i m rank:", rank, "from processor:", name)
