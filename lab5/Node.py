import random
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import grpc
from utils import mod, get_pred, get_succ, ring_between
import zlib
from typing import Callable
import sys
from concurrent import futures
# set the random seed to ZERO for reproducible results
SEED = 0
random.seed(SEED)


class Node(pb2_grpc.NodeServicer):
    # a node needs:
    # 1. an address: ipaddr:port
    # 2. the id of its predecessor
    # 3. finger_table: as described in the assignment
    # 4. a dictionary to save the keys and the corresponding texts
    def __init__(self, address: str, node_id: id, predecessor_id: int, finger_table: set):
        self.address = address
        self.keys_text = {}
        # all these three fields should be assigned after calling register()
        # and then populate_finger_table
        self.node_id = node_id
        self.predecessor_id = predecessor_id
        self.finger_table = finger_table
        # size of the chord
        self.m = 32

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
        print('here')

        succ = get_succ(self.node_id, finger_table.keys())
        print('aa')
        if ring_between(self.predecessor_id, target_id, self.node_id):
            print(1)
            return this_node_callback(request)

        elif ring_between(self.node_id, key, succ):
            print(2)
            succ_address = self.finger_table[succ]
            channel = grpc.insecure_channel(succ_address)
            stub = pb2_grpc.NodeStub(channel)
            
            return eval(f"stub.{operation}")(request)
        
        else:
            print(3)
            target_node = get_pred(target_id, finger_table.keys())
            target_node_address = self.finger_table[target_node]
            channel = grpc.insecure_channel(target_node_address)
            stub = pb2_grpc.NodeStub(channel)
            
            return eval(f"stub.{operation}")(req)
        
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
                    
                # TODO: actually, message should be an int. Talk to Ayhem about comments in *_pb2.py and recompile .proto.
                return pb2.SaveReply(result=True, message=str(self.node_id))

        return self._lookup_and_execute(request, this_node_callback, "save_key")

    def remove_key(self, request, context):
        def this_node_callback(request):
            key = request.key

            if key in self.keys_text.keys():
                del self.keys_text[key]

                # TODO: actually, message should be an int. Talk to Ayhem about comments in *_pb2.py and recompile .proto.
                return pb2.RemoveReply(result=True, message=(str(self.node_id)))
            else:
                return pb2.RemoveReply(result=False, message="No such key")

        return self._lookup_and_execute(request, this_node_callback, "remove_key")

    def find_key(self, request, context):
        def this_node_callback(request):
            key = request.key

            if key in self.keys_text.keys():
                return True, self.node_id, self.address
                
            return True, "No such key"

        return self._lookup_and_execute(request, this_node_callback, "find_key")

    def quit(self, request, context):
        # TODO: implement
        pass

if __name__ == '__main__':
    registry_address = sys.argv[1]
    node_address = sys.argv[2]
    # TODO: only for testing. Should request this from the registry.
    node_id = int(sys.argv[3])
    predecessor_id = int(sys.argv[4])
    finger_table = { 5: node_address }

    # create node object
    node = Node(node_address, node_id, predecessor_id, finger_table)

    # setup and run server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_NodeServicer_to_server(node, server)
    server.add_insecure_port(node_address)
    server.start()
    server.wait_for_termination()