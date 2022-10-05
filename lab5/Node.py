import random
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
from helper_functions import mod


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

    def get_finger_table(self, request, context):
        # the request is created with no fields, so it will be ignored
        # this function will return a copy of the current finger_table saved inside the Node
        return pb2.InfoReply(nodes=self.finger_table.copy())

    def save_key(self, request, context):
        # TODO: implement
        pass

    def remove_key(self, request, context):
        # TODO: implement
        pass

    def find_key(self, request, context):
        # TODO: implement
        pass

    def quit(self, request, context):
        # TODO: implement
        pass
