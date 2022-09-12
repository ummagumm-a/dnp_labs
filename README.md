# DNP Assignments
This repo is a collection of home assignments from Distributed and Network Programming in Innopolis University.
# Lab 1
A reliable transfer protocol on top of UDP. Here client sends a binary file to server. Server should save this file on disk.

To run client: `python lab1/client.py <host>:<port> <filename> <filename_on_server>`

To run server: `python lab1/server.py <port>`

## Dependencies:
* PIL
* tqdm

# Lab 2
A server which maintains a pool of worker threads. On each request it accepts a connection and passes is to the queue. The workers are then responsible for handling the connection.

To run client: `python lab2/client.py <host>:<port>`

To run server: `python lab2/server.py <port>`
