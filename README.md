# CITS3002 Project - 'chriscoins' on Docker 
Project Members: 
- Scott McCormack
- Callum Vidler
- Yau Shing Huang

## Getting the Project Started
To start up this project, follows these steps:
1. Ensure that you have [Docker](https://docs.docker.com/engine/installation/) 
and [Docker Compose](https://docs.docker.com/compose/install/) installed on your local machine.
2. Clone the repository for this project to a local path using the following command: <br>
`git clone https://github.com/ScottMcCormack/CITS3002.git`
3. Run the following Docker Compose command to build the Docker environment: <br>
`docker-compose up` <br>
4. The success of the build will be shown in the console output. 
The following command in another terminal can also be run to show the status of the running containers: <br>
`docker container ls`
## The Docker Environment
Upon successful execution of the previous steps the following images should be pulled from Docker Hub:
- **mongo:latest** (https://hub.docker.com/_/mongo/) <br>
This image provides a running NoSQL MongoDB instance where 'user' and 'blockchain' data 
is stored. Entries are stored and retreived from the MongoDB in a JSON format. 

- **python:3.6** (https://hub.docker.com/_/python/) <br>
This image provides a light python environment in which the Flask applications 
for the Users and Miners are loaded into

Using these images we build the following containers running on a Docker Network:
- **chriscoin_database** (Exposed on [http://localhost:27017](http://localhost:27017)) <br>
A running instance of the MongoDB image that allows connections from the other containers. 
The following databases are used on this instance 
    - **'users'**: Stores registered user credentials with both there public and private keys. <br>
    In principle it is noted that it is not a good idea to store a users private key in this database 
    and would be ideal for a user to store this locally. However for the ease of implementation in this project, 
    it was decided that it would be easier to store this in the MongoDB
    - **blockchain**: Stores the blockchain transactions
    
    We can also connect to and query this database by running a Python script on our host machine. 
    Preliminary testing for this container was achieved by running a Jupyter Notebook on the host machine and 
    using Python Notebook files (.ipynb) to run queries. An example of this is uploaded in the 'notebook' directory at: <br>
    https://github.com/ScottMcCormack/CITS3002/blob/master/notebooks/pymongo_testing.ipynb
- **chriscoin_user01** (Exposed on [http://localhost:5000](http://localhost:5000)) <br>
Web interface for a user (we assume this is **Alice**) that can register, login and transfer chriscoins to other users
- **chriscoin_user02** (Exposed on [http://localhost:5001](http://localhost:5001)) <br>
Same environment as container *'chriscoin_user01'* running in a isolated environment (another container) 
and exposed on a different port (we assume that this is **Bob**)