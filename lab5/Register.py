import random
import sys
from bisect import bisect_left
import grpc
from concurrent import futures

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
from helper_functions import mod

# TODO : MAKE SURE THE CODE ACTUALLY WORKS


# set the random seed to ZERO for reproducible results
SEED = 0
random.seed(SEED)

DEFAULT_PORT = 5555
DEFAULT_M = 5

MAX_WORKERS = 10


# this is the class responsible for the registry's implementation
class Registry(pb2_grpc.RegistryServicer):
    __full_msg = "The chord has reached its maximum capacity"
    __register_msg = "The new node was added to the registry"
    __no_id_msg = "There is no such id in the registry"
    __deregister_msg = "Node deregistered successfully"

    def __init__(self, port: int, m: int):
        # the registry: needs the following fields:
        # port: the port's number
        # m: maximum size of the chord's ring
        # nodes_map: dictionary used to map each id to the node's address: ip:port
        # current: the number of current nodes to facilitate checking
        self.port = port
        self.m = m
        self.max_size = 2 ** m
        self.current = 0
        self.nodes_map = {}

    def __generate_id(self, node_addr: str) -> int:
        """
        given the node's address, this function will verify whether there is space for a new node:
        1. if such space exists, this function returns the new-generated id
        2. if the chord is full return -1
        :param node_addr: the node's address
        :return: -1 or new id
        """
        if self.current < self.max_size:
            while True:
                n_id = random.randint(0, self.max_size - 1)
                if n_id not in self.nodes_map:
                    # increase the number of current nodes
                    self.current += 1
                    # save the node in the map
                    self.nodes_map[n_id] = node_addr
                    # return the node's info
                    return n_id
        else:
            return -1

    def register(self, request, context):
        node_addr = request.addr
        new_id = self.__generate_id(node_addr)
        message = self.__full_msg if new_id < 0 else self.__register_msg
        return pb2.RegisterReply(**{"id": new_id, "message": message})

    def deregister(self, request, context):
        node_id = request.id
        if node_id in self.nodes_map:
            result_tuple = (True, self.__deregister_msg)
        else:
            result_tuple = (False, self.__no_id_msg)
        return pb2.DeregisterReply(**{"result": result_tuple[0], "message": result_tuple[1]})

    def __get_sorted_node_ids(self):
        node_ids = list(self.nodes_map.keys())
        sorted(node_ids)
        return node_ids

    def __successor(self, value, keys_sorted=None):
        if keys_sorted is None:
            keys_sorted = self.__get_sorted_node_ids()

        # if the id passed is larger than the maximum id, then we return the minimum id
        if value > keys_sorted[-1]:
            return keys_sorted[0]
        # otherwise, we can be sure that successor is actually greater than the passed value
        # at the extreme case the successor will be the maximum node in the ring
        for key in keys_sorted:
            if key >= value:
                return key

    def __predecessor(self, node_id, keys_sorted=None):
        if keys_sorted is None:
            keys_sorted = self.__get_sorted_node_ids()

        # this function is only called on node values
        # we can use the following shortcut
        if node_id < keys_sorted[0]:
            return keys_sorted[-1]
        # bisect_left returns the leftmost index where a new value can be inserted while maintaining
        # the order of the iterable, since only one instance of node_id
        # belongs to keys_sorted, bisect_left will return the index of the element just
        # before it in O(logN) time complexity
        return keys_sorted[bisect_left(keys_sorted, node_id)]

    def populate_finger_table(self, request, context):
        # retrieve the id of the node for which the finger table is to be produced
        node_id = request.node_id
        # get a sorted instance of the current node identifiers
        sorted_keys = self.__get_sorted_node_ids()
        # create a set to handle duplicated efficiently
        finger_table = set()
        power_two = 1
        for i in range(self.m):
            # find the successor of ((node_id + 2 ** (m - 1)) % (2 ** m))
            finger_table.add(self.__successor(mod(node_id + power_two, self.max_size), sorted_keys))
            power_two *= 2
        # finds the predecessor
        predecessor_id = self.__predecessor(node_id, sorted_keys)

        # create the map to return with the PopulateReply object
        nodes_map = {}
        for value in finger_table:
            nodes_map[value] = self.nodes_map[value]
        # return the PopulateReply object
        return pb2.PopulateReply(**{"predecessor_id": predecessor_id, "finger_table": nodes_map})

    def get_chord_info(self, request, context):
        # the request is created with no fields, so it will be ignored
        # this function will return a copy of the current map saved inside the Registry
        return pb2.InfoReply(nodes=self.nodes_map.copy())


def main(port: int = DEFAULT_PORT, m: int = DEFAULT_M):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    # set the service of the Registry

    pb2_grpc.add_RegistryServicer_to_server(Registry(port, m), server)

    server.add_insecure_port(f"127.0.0.1:{str(port)}")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 3:
        main(int(args[1]), int(args[2]))
    else:
        main()
