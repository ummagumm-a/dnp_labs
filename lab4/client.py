import service_pb2
import service_pb2_grpc
import grpc
from enum import Enum
import argparse

def parse_query(query):
    temp = query.split()
    query_type = temp[0]
    args = temp[1:]
    if query_type == 'reverse' or query_type == 'split':
        args = ' '.join(args)

        return query_type, args
    elif query_type == 'isprime':
        args = list(map(int, args))

        return query_type, args
    elif query_type == 'exit':
        raise KeyboardInterrupt
    else:
        raise Exception(f"Unknown query type: {query_type}")

def process_query(query_type, args):
    if query_type == 'reverse':
        args = service_pb2.Text(text=args)
        return stub.reverse(args)

    elif query_type == 'split':
        args = service_pb2.TextSplit(text=args, delimiter=' ')
        return stub.split(args)

    elif query_type == 'isprime':
        args = list(map(lambda x: service_pb2.Number(number=x), args))
        return stub.isprime(iter(args))
   
    else:
        raise Exception(f"Unknown query type: {query_type}")

def print_results(query_type, results):
    if query_type == 'reverse':
        print(f'message: {results.text}')
    elif query_type == 'split':
        print(f'number: {results.num_parts}')
        for part in results.parts:
            print(f'parts: {part}')
    elif query_type == 'isprime':
        for res in results:
            (num, is_prime) = res.number, res.isprime
            if is_prime:
                print(f'{num} is prime')
            else:
                print(f'{num} is not prime')
    else:
        raise Exception(f"Unknown query type: {query_type}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    channel = grpc.insecure_channel(f'127.0.0.1:{args.port}')
    stub = service_pb2_grpc.ServiceStub(channel)

    try:
        while True:
            query = input('> ')
            query_type, args = parse_query(query)
            results = process_query(query_type, args)
            print_results(query_type, results)
    except KeyboardInterrupt:
        print('Shutting down')
