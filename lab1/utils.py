import socket

def try_n_times(retries, callback):
    i = 0
    while i < retries:
        try:
            return callback()
        except socket.timeout:
            i += 1
    else:
        raise Exception('Number of retries exceeded.')
        
def split_data(data, buf_size):
    i = 0
    parts = []
    while i * buf_size < len(data):
        part = data[i * buf_size:(i + 1) * buf_size]
        parts.append(part)
        i += 1
    
    return parts

def initialize_socket(address='', port=0, timeout=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if timeout is not None:
        s.settimeout(timeout)
    s.bind((address, port))
    
    return s