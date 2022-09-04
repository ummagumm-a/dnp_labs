import socket
import io
from PIL import Image
from utils import *
import argparse
from tqdm import tqdm
import logging
from message import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUF_SIZE = 1024
DATA_HEADER_SIZE = 20
RETRIES = 5
TIMEOUT = 0.5 


def load_jpg_image_return_binary(path):
    img = Image.open(path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def connect_to_server(s, data, on_server_filename, server_address):
    start_message = make_start_message(on_server_filename, len(data))
    
    def helper():
        while True:
            s.sendto(start_message, server_address)
            value, address = s.recvfrom(BUF_SIZE)
            if address != server_address: continue
            else: return value
            
    value = try_n_times(RETRIES, helper)
    
    next_seqno, buf_size = parse_init_ack(value)
    if next_seqno != 1:
        raise Exception(f'Wrong next_seqno on session start. Returned next_seqno={next_seqno} (not 1).')
        
    return buf_size

def send_part(s, part, cur_seqno, server_address):
    def helper():
        while True:
            s.sendto(part, server_address)
            message, address = s.recvfrom(BUF_SIZE)
            if address != server_address: continue
            else:
                return parse_data_ack(message)
            
    next_seqno = -1
    while next_seqno != cur_seqno + 1:
        next_seqno = try_n_times(RETRIES, helper)

def send_data(data, on_server_filename, server_address):
    logger.info(f'Data length is {len(data)}.')
    s = initialize_socket(timeout=TIMEOUT)
    try:
        buf_size = connect_to_server(s, data, on_server_filename, server_address)
    except Exception as e:
        logger.error(f'{e} Aborting...')
        return
        
    logger.info('CONNECTED SUCCESSFULLY')
    logger.info(f'buffer size is {buf_size}')
    
    data_parts = split_data(data, buf_size - DATA_HEADER_SIZE)
    logger.info(f'Data is split in {len(data_parts)} parts.')
    
    try:
        logger.info('Starting to transfer data parts.')
        cur_seqno = 1
        for part in tqdm(data_parts):
            msg = make_data_message(cur_seqno, part)
            send_part(s, msg, cur_seqno, server_address)
            cur_seqno += 1
        logger.info('Successfully transfered the file.')
    except Exception as e:
        logger.error(f'{e} Aborting...')
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server_address', type=str)
    parser.add_argument('origin_filename')
    parser.add_argument('destination_filename')
    args = parser.parse_args()
    
    # parse server_address
    server_host, server_port = args.server_address.split(':')
    server_port = int(server_port)
    
    # set logging level
    logging.basicConfig(level=logging.INFO)

    # load image
    data = load_jpg_image_return_binary(args.origin_filename)
    
    send_data(data, args.destination_filename, (server_host, server_port))
