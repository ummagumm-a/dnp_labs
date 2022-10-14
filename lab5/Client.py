import sys
import grpc
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
from typing import Callable
import re

class ClientConnection:
    def __init__(self):
        self.server_type = None
        self.stub = None

    def _stub_type_check_and_execute(self, node_callback: Callable, registry_callback: Callable):
        """
        Checks the validity of the stub's type and performs appropriate operation depending on the type.

        :params node_callback:
        """
        if self.stub is None:
            raise Exception("Connection is not created yet.")
        elif isinstance(self.stub, pb2_grpc.NodeStub):
            return node_callback()
        elif isinstance(self.stub, pb2_grpc.RegistryStub):
            return registry_callback()
        else:
            raise Exception(f"Weird stub type: {type(self.stub)}.")
        
    def connect(self, ipaddr: str, port: int):
        """
        Connect to a node or a registry with given address. 
        If connection is successful - stub is initialized and saved. Otherwise, raises an exception.

        TODO: Should distinguish between node and registry. Now connects only to nodes.
        """

        # try:
        #     channel = grpc.insecure_channel(f'{ipaddr}:{port}')
        #     self.stub = pb2_grpc.NodeStub(channel)

        #     return "Connected sucessfully"
        # except:
        #     raise Exception(f"Couldn't create a connection to {ipaddr}:{port}.")
        # TODO: these exceptions will not work because the code doesn't throw an error when creating NodeStub with Registry's IP:PORT
        channel = grpc.insecure_channel(f'{ipaddr}:{port}')
        try:
            # set the reverse service
            self.stub = pb2_grpc.NodeStub(channel)

            return "Connected sucessfully"
        except Exception:
            try:
                self.stub = pb2_grpc.RegistryStub(channel)
            except:
                raise Exception(f"Couldn't create a connection to {ipaddr}:{port}.")

    def get_info(self):
        """
        If is connected to a node - return finger table.
        If is connected to a registy - return chord info.

        Both in string representation. This function is only used for visualization purposes.
        """
        def node_callback():
            return str(self.stub.get_finger_table(pb2.InfoRequest()))

        def registry_callback():
            return str(self.stub.get_chord_info(pb2.InfoRequest()))
        
        return self._stub_type_check_and_execute(node_callback, registry_callback)

    def save(self, key: str, text: str):
        """
        Saves a key-value pair into Chord.

        Returns message about success of performed operation.

        :params key: key
        :params text: value
        """
        def node_callback():
            save_request = pb2.SaveRequest(key=key, text=text)
            response = self.stub.save_key(save_request)

            return response.node_id if response.result else response.error_message

        def registry_callback():
            raise Exception("Can't save this data. The client is connected to a registry.")

        return self._stub_type_check_and_execute(node_callback, registry_callback)
    
    def remove(self, key: str):
        """
        Remove a key-value pair from Chord.

        Returns message about success of performed operation.

        :params key: key
        """
        def node_callback():
            remove_request = pb2.RemoveRequest(key=key)
            response = self.stub.remove_key(remove_request)

            return response.node_id if response.result else response.error_message

        def registry_callback():
            raise Exception("Can't remove this key. The client is connected to a registry.")

        return self._stub_type_check_and_execute(node_callback, registry_callback)

    def find(self, key):
        """
        Finds a value by key in Chord.
        If operation is success - returns the text. Otherwise, returns an error message.

        :params key: key
        """
        def node_callback():
            find_request = pb2.FindRequest(key=key)
            response = self.stub.find_key(find_request)

            return response.node if response.result else response.error_message

        def registry_callback():
            raise Exception("Can't find this key. The client is connected to a registry.")

        return self._stub_type_check_and_execute(node_callback, registry_callback)

def make_args(match: re.Match):
    """
    Creates a list of arguments parsed from matched string.
    """
    args = []
    i = 2
    while True:
        try:
            arg = match.group(i)
        except:
            return args
        i += 1
        args.append(arg)


def parse_input(inp: str):
    """
    Accepts an input string and returns query with arguments.
    """
    # List patterns of acceptable messages
    connect_regex = r"(connect) (\d+\.\d+\.\d+\.\d+):(\d+)"
    get_info_regex = r"(get_info)"
    save_regex = r'(save)\s+"(.*)" (.*)'
    remove_regex = r'(remove)\s+"(.*)"'
    find_regex = r'(find)\s+"(.*)"'

    # Compile them into regex patterns
    patterns = [connect_regex, get_info_regex, save_regex, remove_regex, find_regex]

    # Check each pattern
    for pattern in patterns:
        match = re.fullmatch(pattern, inp)
        # If matched successfully
        if match is not None:
            return match[1], make_args(match)
    
    return None, None


def cli_loop():
    client_connection = ClientConnection()

    while True:
        inp = input("> ")
        if inp == 'exit':
            break
        query, args = parse_input(inp)
        if query is None:
            print("Incorrect Query")
            continue
        res = eval(f'client_connection.{query}')(*args)
        print(res)


if __name__ == '__main__':
    cli_loop()


