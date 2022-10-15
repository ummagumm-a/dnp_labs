import random
import sys
import zlib
from concurrent import futures
from threading import Thread, Event
from time import sleep
from typing import Callable

import grpc

import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
from utils import get_index_of_next_node, ring_between

# set the random seed to ZERO for reproducible results
SEED = 0
random.seed(SEED)
SLEEP_TIME = 1

class Node(pb2_grpc.NodeServicer):
    pass


def poll_finger_table_updates(obj: Node, run_event: Event):
    while run_event.is_set():
        request = pb2.PopulateRequest(node_id=obj.node_id)
        response = obj.registry_stub.populate_finger_table(request)
        obj.predecessor = response.predecessor
        # the response.finger_table is an immutable iterable object, that can't have its elements assigned.
        # it should be iterated through so the elements can be assigned freely afterwards: without ERRORS
        obj.finger_table = [ft for ft in response.finger_table]


        print("#" * 50)
        print(f"Node's id: {str(obj.node_id)}")
        print(f"predecessor: {str(obj.predecessor.node_id)}")
        for i in range(len(obj.finger_table)):
            print(f"{str(i)}: node id:{str(obj.finger_table[i].node_id)}, address: {str(obj.finger_table[i].address)}")

        print("CURRENT KEYS: " + "#" * 40)
        print([(key, text, obj.encode_key(key)) for key, text in obj.keys_text.items()])

        sleep(SLEEP_TIME)


class Node(pb2_grpc.NodeServicer):
    # a node needs:
    # 1. an address: ipaddr:port
    # 2. the id of its predecessor
    # 3. finger_table: as described in the assignment
    # 4. a dictionary to save the keys and the corresponding texts
    def __init__(self, node_address: str, registry_address: str):
        self.node_address = node_address
        self.registry_address = registry_address
        self.keys_text = {}
        self.registry_stub, self.node_id, self.m, self.finger_table, self.predecessor = self._initialize()
        # after obtaining the node_id, predecessor and finger_table, the node is ready to request
        # the keys from its successor
        self.get_keys_successor()

        self.poller_handler, self.run_event = self._poll_finger_table_updates_spawn()

    def _initialize(self) -> (pb2_grpc.RegistryStub, int, int, list[pb2.FingerTableEntry], pb2.FingerTableEntry):
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
        # keep in mind that the response.predecessor is a FingerTableEntry object
        predecessor = response.predecessor

        # keep in mind that response.finger_table is an array of FingerTableEntry objects
        finger_table = [ft for ft in response.finger_table]
        # added for debugging purposes
        for i in range(len(finger_table)):
            print(f"{str(i)}: node id:{str(finger_table[i].node_id)}, address: {str(finger_table[i].address)}")
        return registry_stub, node_id, m, finger_table, predecessor

    def _poll_finger_table_updates_spawn(self):
        run_event = Event()
        run_event.set()

        handler = Thread(target=poll_finger_table_updates, args=(self, run_event))
        handler.start()
        return handler, run_event

    def get_finger_table(self, request, context):
        # the request is created with no fields, so it will be ignored
        # this function will return a copy of the current finger_table saved inside the Node
        return pb2.InfoReply(nodes=self.finger_table)

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
        # assign id for this key
        key_id = self.encode_key(key)

        # successor id of current node
        succ = self.finger_table[0].node_id

        # if there is only one node in the chord
        # or key should be stored in current node
        if self.predecessor.node_id == self.node_id or \
                ring_between(self.predecessor.node_id, key_id, self.node_id):
            return this_node_callback(request)

        # if key should be stored in successor node
        elif ring_between(self.node_id, key_id, succ):
            # extract successor's address
            succ_address = self.finger_table[0].address
            # create connection to successor
            channel = grpc.insecure_channel(succ_address)
            stub = pb2_grpc.NodeStub(channel)

            # forward request to successor
            return eval(f"stub.{operation}")(request)

        else:
            # get list of available node ids
            finger_table_node_ids = [x.node_id for x in self.finger_table]
            # get id of next node to forward request to
            target_node_id = get_index_of_next_node(key_id, finger_table_node_ids)
            # get its address
            target_node_address = self.finger_table[target_node_id].address
            # create connection with next node
            channel = grpc.insecure_channel(target_node_address)
            stub = pb2_grpc.NodeStub(channel)

            # forward request to next node
            return eval(f"stub.{operation}")(request)

    def encode_key(self, key):
        """
        Map key into position on the chord.
        """
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
                return pb2.FindReply(result=True, node=pb2.FingerTableEntry(node_id=self.node_id, address=self.node_address))

            return pb2.FindReply(result=False, error_message="No such key")

        return self._lookup_and_execute(request, this_node_callback, "find_key")

    def predecessor_notification(self, request, context):
        """
        this function is created so that a node changes its successor when its original accessor leaves the chord
        :param request: the NotificationRequest object
        :param context:
        :return: nothing, set the new value accordingly
        """
        node_id = request.new_neighbor.node_id
        address = request.new_neighbor.address
        try:
            # the new successor is the first value in the finger table
            self.finger_table[0] = pb2.FingerTableEntry(node_id=node_id, address=address)
            return pb2.NotificationReply(result=True)
        except:
            return pb2.NotificationReply(result=False)

    def successor_notification(self, request, context):
        """
        This function is created so that a node changes its predecessor when its original predecessor leaves the chord
        :param request: Notification requist
        :param context:
        :return: nothing, set the new value accordingly
        """
        try:
            # the predecessor is set separately as a field
            self.predecessor = request.new_neighbor
            return pb2.NotificationReply(result=True)
        except:
            return pb2.NotificationReply(result=False)

    def quit(self, request, context):
        """
        This method is created to remove a node from the chord correctly. This is implemented through the following
        steps:
        0. stop the polling thread
        1. set the predecessor of the successor node to the predecessor of the current node
        2. set the successor of the predecessor node to the successor of the current node
        3. save all the current keys in the successor
        4. ask the register to deregister the node
        :param request: request from user: does not contain any information:
        :param context:
        :return: nothing
        """

        # step 0
        self.run_event.clear()
        self.poller_handler.join()

        # step 1
        successor_address = self.finger_table[0].address  # , can be replaced with self.finger_table[0][1]

        if successor_address != self.node_address:
            print("THIS NODE IS THE ONLY NODE IN THE CHORD: CAN'T GET RID OF IT.")
            # set the channel of communication
            channel_successor = grpc.insecure_channel(successor_address)
            # create the client
            stub_successor = pb2_grpc.NodeStub(channel_successor)
            # notify the successor
            notification = pb2.NotificationRequest(new_neighbor=self.predecessor)
            # receive notification
            notification_reply = stub_successor.successor_notification(notification)

            if not notification_reply.result:
                print("THE SUCCESSOR COULD NOT SET ITS PREDECESSOR SUCCESSFULLY. ABORTING!!")
                return

            # step 2
            channel_predecessor = grpc.insecure_channel(self.predecessor.address)
            stub_predecessor = pb2_grpc.NodeStub(channel_predecessor)
            notification = pb2.NotificationRequest(new_neighbor=self.finger_table[0])
            notification_reply = stub_predecessor.predecessor_notification(notification)

            if not notification_reply.result:
                print("THE PREDECESSOR COULD NOT SET ITS SUCCESSOR SUCCESSFULLY. ABORTING!!")
                return

        # step 3 pass all the current keys to the successor
            for key, text in self.keys_text.copy().items():
                # ask successor to save the key
                stub_successor.save_key(pb2.SaveRequest(key=key, text=text))

                # if not save_reply.result:
                #     print(f"THE SUCCESSOR COULD NOT SAVE THE PIECE OF {text} associated with key {key}. ABORTING!!")

                # remove the pair <key, text> locally
                self.keys_text.pop(key)

            # print if it is empty
            assert not self.keys_text

        # step 4: contacting the registry to deregister the node
        # we use the registryStud created in the initialization phase
        deregister_req = pb2.DeregisterRequest(node_id=self.node_id)
        deregister_reply = self.registry_stub.deregister(deregister_req)

        # print the message from registry!!!
        print(deregister_reply.message)

        sys.exit()

    # this function is executed by a successor node. The successor Node will play the role of a server
    # while the newly-added node will play the role of a client. For this reason, a new function is needed
    # to write the client part of the code.
    def distributeKeys(self, request, context):
        """
        This method distributes the keys as follows:
        the request contains the id of the new node (ID)
        All keys that are less or equal to ID and strictly larger than the id of the predecessor
        will be distributed to the new node.
        :param request: request contains the id and address of the new node
        :param context:
        :return: an array of FingerTableEntry objects containing keys (and their corresponding texts) that should
        be moved to the new node.
        """
        # extract the id of the new node
        new_node_id = request.new_node.node_id
        print(f"RECEIVED REQUEST FROM {str(new_node_id)}, address: {request.new_node.address}")
        # filter the keys that should be stored in the new node: found based on the mathematical expression below
        distributed_keys = [pb2.SaveRequest(key=key, text=value) for key, value in self.keys_text.items()
                            if ring_between(self.predecessor.node_id, self.encode_key(key), new_node_id)]

        print("before distributing")
        # print keys before deleting keys
        print([(key, text, self.encode_key(key)) for key, text in self.keys_text.items()])

        # delete the keys that should be transferred
        for save_request in distributed_keys:
            self.keys_text.pop(save_request.key)
        print("after distributing")
        # print keys after deleting keys
        print([(key, text, self.encode_key(key)) for key, text in self.keys_text.items()])

        # send the result
        return pb2.DistributeReply(moved_keys=distributed_keys)

    # this function represents the client code that will code distributeKeys
    def get_keys_successor(self):
        # get the successor address
        successor_address = self.finger_table[0].address
        # ignore this step if this node is the only node present in the chord
        if successor_address == self.node_address:
            return

        # connect to the successor
        # create a request to send
        while True:
            try:
                channel = grpc.insecure_channel(successor_address, options=(('grpc.enable_http_proxy', 0),))
                stub = pb2_grpc.NodeStub(channel)
                keysRequest = pb2.DistributeRequest(new_node=
                                                    pb2.FingerTableEntry(node_id=self.node_id,
                                                                         address=self.node_address))

                print(f"SENT REQUEST TO {successor_address}, id: {str(self.finger_table[0].node_id)}")
                # receive the keys that should be deleted
                keysReply = stub.distributeKeys(keysRequest)
                break
            except:
                print("SOME ERROR OCCURED WHEN ACQUIRING THE KEYS: RECONNECTING")

        # the received object is a KeysRequest object with one field moved_keys which is an array of SaveRequest objects
        # each containing key and text fields
        print("new keys")
        print([(SR.key, SR.text) for SR in keysReply.moved_keys])

        for SR in keysReply.moved_keys:
            self.keys_text[SR.key] = SR.text

    def checkConnection(self, request, context):
        """
        Return type of this process (e.g. whether it is a registry or a node).
        """
        return pb2.CheckConnectionReply()


if __name__ == '__main__':

    registry_address = sys.argv[1]
    node_address = sys.argv[2]

    # create node object
    node = Node(node_address, registry_address)
    try:
        # setup and run server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_NodeServicer_to_server(node, server)
        server.add_insecure_port(node_address)
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("QUITTING. GOOD BYE")
        node.quit(None, None)
