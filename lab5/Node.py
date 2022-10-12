import random
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import grpc
from utils import mod, get_pred, get_succ, ring_between
import zlib
from typing import Callable
import sys
from concurrent import futures
from threading import Thread
from time import sleep
# set the random seed to ZERO for reproducible results
SEED = 0
random.seed(SEED)


class Node(pb2_grpc.NodeServicer):
    """
    """
    # a node needs:
    # 1. an address: ipaddr:port
    # 2. the id of its predecessor
    # 3. finger_table: as described in the assignment
    # 4. a dictionary to save the keys and the corresponding texts
    def __init__(self, node_address: str, registry_address: str):
        self.node_address = node_address
        self.registry_address = registry_address
        self.keys_text = {}
        self.registry_stub, self.node_id, self.m, \
                            self.finger_table, self.predecessor = self._initialize_variables()
        self.poller_handler = self._poll_finger_table_updates_spawn()
        self._notify_neighbors()

    def _initialize_variables(self) -> (pb2_grpc.RegistryStub, int, int, list[(int, str)], pb2.FingerTableEntry):
        """
        This function initializes all important fields and registers itself in the registry.
        """

        # Create registry stub
        channel = grpc.insecure_channel(self.registry_address)
        registry_stub = pb2_grpc.RegistryStub(channel)

        # Register itself
        response = registry_stub.register(pb2.RegisterRequest(address=self.node_address))
        node_id, m = response.id, response.m

        # Poll finger table and predecessor
        request = pb2.PopulateRequest(node_id=node_id)
        response = registry_stub.populate_finger_table(request)
        predecessor = response.predecessor
        finger_table = response.finger_table

        return registry_stub, node_id, m, finger_table, predecessor

    def _poll_finger_table_updates_spawn(self):
        handler = Thread(target=poll_finger_table_updates, args=(self,))
        handler.start()
        return handler

    def _notify_neighbors(self):
        pass

    def get_finger_table(self, request, context):
        # the request is created with no fields, so it will be ignored
        # this function will return a copy of the current finger_table saved inside the Node
        return pb2.InfoReply(nodes=self.finger_table.copy())

    def _lookup_and_execute(self, request, this_node_callback: Callable, operation: str):
        """
        This function finds a node responsible for key from 'request' and performs some operations.
        If responsible node is the current one - call 'this_node_callback'.
        If successor is responsible - call 'operation' on the successor.
        Otherwise, find predecessor of id obtained from the key, and call 'operation' on this node.

        :params request: request which requires processing. Should contain field 'key'.
        :params this_node_callback: manipulations with dict 'self.keys_text' that need to be performed in response to the request. 
                                    Called in case this node is responsible for key from the request.
        :params operation: function that needs to be called on another node for key responsible for key from the request.
        """

        key = request.key
        target_id = self.encode_key(key)

        # succ = get_succ(self.node_id, finger_table.keys())
        succ = self.finger_table[0].node_id
        if ring_between(self.predecessor.node_id, target_id, self.node_id):
            return this_node_callback(request)

        elif ring_between(self.node_id, key, succ):
            succ_address = self.finger_table[succ]
            channel = grpc.insecure_channel(succ_address)
            stub = pb2_grpc.NodeStub(channel)
            
            return eval(f"stub.{operation}")(request)
        
        else:
            finger_table_node_ids = list(map(lambda x: x[0], self.finger_table))
            target_node_index = get_pred(target_id, finger_table_node_ids)
            target_node_address = self.finger_table[target_node_index]
            channel = grpc.insecure_channel(target_node_address)
            stub = pb2_grpc.NodeStub(channel)
            
            return eval(f"stub.{operation}")(request)
        
    def encode_key(self, key):
        hash_value = zlib.adler32(key.encode())
        target_id = hash_value % 2 ** self.m

        return target_id

    def save_key(self, request, context):
        def this_node_callback(request: pb2.SaveRequest):
            key, text = request.key, request.text

            if key in self.keys_text.keys():
                return pb2.SaveReply(result=False, error_message="Key already exists.")
            else:
                self.keys_text[key] = text
                    
                return pb2.SaveReply(result=True, node_id=self.node_id)

        return self._lookup_and_execute(request, this_node_callback, "save_key")

    def remove_key(self, request, context):
        def this_node_callback(request):
            key = request.key

            if key in self.keys_text.keys():
                del self.keys_text[key]

                return pb2.RemoveReply(result=True, node_id=self.node_id)
            else:
                return pb2.RemoveReply(result=False, error_message="No such key")

        return self._lookup_and_execute(request, this_node_callback, "remove_key")

    def find_key(self, request, context):
        def this_node_callback(request):
            key = request.key

            if key in self.keys_text.keys():

                return pb2.FindReply(result=True, node=pb2.FingerTableEntry(node_id=self.node_id, address=self.address))
                
            return pb2.FindReply(result=True, error_message="No such key")

        return self._lookup_and_execute(request, this_node_callback, "find_key")

    def quit(self, request, context):
        # TODO: implement
        pass


def poll_finger_table_updates(obj: Node):
    while True:
        request = pb2.PopulateRequest(node_id=obj.node_id)
        response = obj.registry_stub.populate_finger_table(request)
        obj.predecessor = response.predecessor
        obj.finger_table = response.finger_table
        sleep(1)


if __name__ == '__main__':
    registry_address = sys.argv[1]
    node_address = sys.argv[2]

    # create node object
    node = Node(node_address, registry_address)

    # setup and run server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_NodeServicer_to_server(node, server)
    server.add_insecure_port(node_address)
    server.start()
    server.wait_for_termination()