import random
import sys
from bisect import bisect_left
import grpc
from concurrent import futures

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
from utils import mod

# TODO : MAKE SURE THE CODE ACTUALLY WORKS


# set the random seed to ZERO for reproducible results
SEED = 0
random.seed(SEED)

DEFAULT_ADDRESS = "127.0.0.1:5000"
DEFAULT_PORT = 5555
DEFAULT_M = 5

MAX_WORKERS = 10


# this is the class responsible for the registry's implementation
class Registry(pb2_grpc.RegistryServicer):
    __full_msg = "The chord has reached its maximum capacity"
    __register_msg = "The new node was added to the registry"
    __no_id_msg = "There is no such id in the registry"
    __deregister_msg = "Node deregistered successfully"

    def __init__(self, address: str, m: int):
        # the registry: needs the following fields:
        # port: the port's number
        # m: maximum size of the chord's ring
        # nodes_map: dictionary used to map each id to the node's address: ip:port
        # current: the number of current nodes to facilitate checking
        self.address = address
        self.m = m
        self.max_size = 2 ** m
        # dictionary of id and address port pairs for all registered nodes
        self.nodes_map = {}

    def __generate_id(self) -> int:
        """
        given the node's address, this function will verify whether there is space for a new node:
        1. if such space exists, this function returns the new-generated id
        2. if the chord is full return -1
        :return: -1 or new id
        """
        if len(self.nodes_map) < self.max_size:
            while True:
                n_id = random.randint(0, self.max_size - 1)
                if n_id not in self.nodes_map:
                    # return the node's info
                    return n_id
        else:
            return -1

    def register(self, request, context):
        node_addr = request.address
        new_id = self.__generate_id()

        if new_id < 0:
            return pb2.RegisterReply(id=new_id, error_message=self.__full_msg)
        # save the node in the map
        self.nodes_map[new_id] = node_addr
        return pb2.RegisterReply(id=new_id, m=self.m)

    def deregister(self, request, context):
        node_id = request.node_id
        if node_id in self.nodes_map:
            result_tuple = (True, self.__deregister_msg)
            # remove the actual node id
            self.nodes_map.pop(node_id)
        else:
            result_tuple = (False, self.__no_id_msg)
        return pb2.DeregisterRequest(result=result_tuple[0], message=result_tuple[1])

    def __get_sorted_node_ids(self):
        node_ids = list(self.nodes_map.keys())
        return sorted(node_ids)

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
        if node_id <= keys_sorted[0]:
            return keys_sorted[-1]
        # bisect_left returns the leftmost index where a new value can be inserted while maintaining
        # the order of the iterable, since only one instance of node_id
        # belongs to keys_sorted, bisect_left will return the index of the element just
        # before it in O(logN) time complexity
        index = bisect_left(keys_sorted, node_id)
        return keys_sorted[index - 1]

    def populate_finger_table(self, request, context):
        # retrieve the id of the node for which the finger table is to be produced
        node_id = request.node_id
        # get a sorted instance of the current node identifiers
        sorted_keys = self.__get_sorted_node_ids()
        # create a set to handle duplicated efficiently
        finger_table_keys = set()
        # create a FingerTableEntry object for the predecessor id
        predecessor_id = self.__predecessor(node_id, sorted_keys)
        ft_entry_predecessor = pb2.FingerTableEntry(node_id=predecessor_id, address=self.nodes_map[predecessor_id])

        # create a list to save FingerTableEntry objects corresponding to the rest of the nodes
        finger_table = []
        power_two = 1

        for i in range(self.m):
            # find the successor of ((node_id + 2 ** (m - 1)) % (2 ** m))
            new_id = self.__successor(mod(node_id + power_two, self.max_size), sorted_keys)
            # if the new calculated id is not in the set of unique ids, then add it
            if new_id not in finger_table_keys:
                new_finger_table_entry = pb2.FingerTableEntry(node_id=new_id, address=self.nodes_map[new_id])
                finger_table.append(new_finger_table_entry)
                # add the new id to the keys to avoid duplicates
                finger_table_keys.add(new_id)
            power_two *= 2

        # return the PopulateReply object
        return pb2.PopulateReply(predecessor=ft_entry_predecessor, finger_table=finger_table)

    def get_chord_info(self, request, context):
        # the request is created with no fields, so it will be ignored
        # this function will return a copy of the current map saved inside the Registry
        return pb2.InfoReply(nodes=self.nodes_map.copy())


def main(address: str = DEFAULT_ADDRESS, m: int = DEFAULT_M):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    # set the service of the Registry

    pb2_grpc.add_RegistryServicer_to_server(Registry(address, m), server)

    server.add_insecure_port(address)
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 3:
        main(args[1], int(args[2]))
    else:
        main()