DELIMITER = ' | '

def type_of_message(message):
    message_type = message.split(' | '.encode(), 1)[0].decode()
    
    if len(message_type) == 1 and message_type in 'sad':
        return message_type
    else:
        raise Exception(f"Unknown message type: {message_type}")

def validate_message(obtained_type, required_type):
    if obtained_type != required_type:
        raise Exception(f'Message is not an {required_type}-type. Obtained type is {obtained_type}')
        
def make_start_message(filename, total_size):
    return f's | 0 | {filename} | {total_size}'.encode()

def parse_start_message(message):
    message = message.decode()
    s, seqno, filename, total_size = message.split(DELIMITER)
    validate_message(s, 's')
    
    return s, int(seqno), filename, int(total_size)

def make_data_message(seqno, data_bytes):
    return f'd | {seqno} | '.encode() + data_bytes

def parse_data_message(message):
#     message = message.decode()
    d, seqno, data_bytes = message.split(DELIMITER.encode())
    validate_message(d.decode(), 'd')
    
    return int(seqno.decode()), data_bytes

def parse_init_ack(message):
    message = message.decode()
    
    a, next_seqno, buf_size = message.split(DELIMITER)
    validate_message(a, 'a')
    
    return int(next_seqno), int(buf_size)

def parse_data_ack(message):
    message = message.decode()
    
    a, next_seqno = message.split(DELIMITER)
    validate_message(a, 'a')
    
    return int(next_seqno)

def make_start_ack(next_seqno, buf_size):
    return f'a | {next_seqno} | {buf_size}'.encode()

def make_data_ack(next_seqno):
    return f'a | {next_seqno}'.encode()

