import socket
import asyncio
import argparse
import time
import logging
from utils import *
from message import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SERVER_HOST = '127.0.0.1'
BUF_SIZE = 1024

class Session:
    def __init__(self, seqno0, filename, expected_data_size, idle_max_time=3000):
        self.next_seqno = seqno0 + 1
        self.filename = filename
        self.expected_data_size = expected_data_size
        self.received_data = b''
        self.last_reception_timestamp = time.time()
        self.idle_max_time = idle_max_time
        
    def check_seqno(self, seqno):
        return seqno == self.next_seqno
    
    def add_data(self, seqno, new_data_chunk):
        self.next_seqno = seqno + 1
        self.received_data += new_data_chunk
        self.received_data = self.received_data[:self.expected_data_size]
        self.last_reception_timestamp = time.time()
        
        if len(self.received_data) == self.expected_data_size:
            return True
        else:
            return False
        
    def save_data(self):
        with open(self.filename, 'wb+') as f:
            f.write(self.received_data)
            
    def is_idle(self):
        return time.time() - self.last_reception_timestamp > self.idle_max_time
        
state_tracker = {} # key - (CLIENT_HOST, CLIENT_PORT); value - Session

def close_session(address):
    logger.info(f'Transfer finished. Saving data sent by {address}...')
    state_tracker[address].save_data()
    del state_tracker[address]
    logger.info('Saved successfully. Session removed.')
    
def handle_start_message(stream):
    message, address = stream
    _, seqno, filename, total_size = parse_start_message(message)

    if address not in state_tracker.keys():
        state_tracker[address] = Session(seqno, filename, total_size)
        logger.info(f"Created new session with {address}")
    elif not state_tracker[address].check_seqno(seqno + 1): # if session with 'address' already exist, 
                                                            # and client sends start message 
                                                            # with different seqno compared to previous
        raise Exception(f"Session with {address} already exists.")
    
    return make_start_ack(seqno + 1, BUF_SIZE)
    
def handle_data_message(stream):
    message, address = stream
    
    seqno, data_bytes = parse_data_message(message)
    
    no_more = False
    if state_tracker[address].check_seqno(seqno):
        no_more = state_tracker[address].add_data(seqno, data_bytes)
        
    ack = make_data_ack(state_tracker[address].next_seqno)
    
    if no_more:
        close_session(address)
        
    return ack

async def handle_message(s, stream):
    value, address = stream
    message_type = type_of_message(value)
    if message_type == 's':
        ack = handle_start_message(stream)
    elif message_type == 'd':
        ack = handle_data_message(stream)
    else:
        raise Exception(f"Unsupported message type {message_type}.")
        
    if ack is not None:
        s.sendto(ack, address)
        
def remove_idle_connections():
    to_remove = []
    for (address, session) in state_tracker.items():
        if session.is_idle():
            to_remove.append(address)
            
    for address in to_remove:
        del state_tracker[address]     

async def run_server(server_port):
    s = initialize_socket(SERVER_HOST, server_port, timeout=None)
    logger.info(f'Server started at {SERVER_HOST}:{server_port}.')
    while True:
        stream = s.recvfrom(BUF_SIZE)
        await handle_message(s, stream)
        remove_idle_connections()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port', type=int)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_server(args.server_port))
