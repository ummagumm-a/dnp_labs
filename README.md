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

# Lab 3
**ZeroMQ** is used here.

A chat application. There are two workers which offer different services and work by subscription on message patterns. If a client writes a message 'isprime 7', it will be directed to a worker and the result returned to all clients.

* primer.py: subscribes on 'isprime ...' pattern. Returns whether number is prime.
* gcd.py: subscribes on 'gcd ...' pattern. Return gcd of two numbers.

# Lab 4
**gRPC** is used here.

Client CLI offers following functions: `reverse <text>`, `split <text>`, `isprime <num> <num> ...`. Appropriate functions will be called for all of these queries. But what's important is that they will be actually executed on a server.
