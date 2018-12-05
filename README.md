# DiNo 
 
 DiNo is a decentralized peer to peer framework for running parallel applications on a cluster of commodity computers. It allows nodes to join the cluster and share their resources with other nodes and use their resources in turn for blazing fast computation. 
     
## Inside the package
DiNo is a pythonian framework. It comes with a web server, a command line interface and a parallel library. A helper script is also included to install necessary dependencies and prepare the environment for usage. DiNo relies on MPI to do  parallel computation.

## How it works?
The web server is used to join the cluster. When a node runs the server and initializes using the command line. It pings the other nodes and everyone updates their database with this node's IP address. <br> <br>
Once the node is live, the user can write a simple code and use DiNo's library functions to execute the job in parallel. For example,
```python
A = np.round(np.random.rand(5, 10)*100)
B= np.round(np.random.rand(10, 2)*100)
C = matmul(A, B) # function call
print(C)
```
When executed, the DiNo interpreter adds the function call's definition in the file and synchronizes with other nodes for execution. <br><br>
The server executes a background polling service to remove dead nodes from its database.

## Running

Requirements: Linux (Debian), python3, git.

#### Clone the repository
`$ git clone https://github.com/shubham1172/dino` <br>
`$ cd dino`

#### Install dependencies 
`$ bash install.sh` <br>
`$ python3 src/create_db.py`

#### Joining the cluster
The DiNo web server must be started and initialized. <br> <br>
`$ python3 src/dinoserver.py` <br>
`$ python3 src/dino.py init`

#### List connected nodes
`$ python3 src/dino.py listall`

#### Running your code
`$ python3 src/dino.py mpirun file.py`

## Future work
- The entire dependency issues will be sorted once we move to Docker.
- Include option to update SSH keys between nodes.

## Contributors
[@anujanegi](https://github.com/anujanegi) <br>
[@kunalchandiramani](https://github.com/kunalchandiramani) <br>
[@shubham1172](https://github.com/shubham1172)
