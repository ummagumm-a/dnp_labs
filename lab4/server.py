import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import argparse

def _is_prime(n):                                                           
    if n in (2, 3):                                                        
        return True                                                        
    if n % 2 == 0:                                                         
        return False                                                       
    for divisor in range(3, n, 2):                                         
        if n % divisor == 0:
            return False
    return True

class Service(service_pb2_grpc.ServiceServicer):
    def reverse(self, request, context):
        return service_pb2.Text(text=request.text[::-1])

    def split(self, request, context):
        text_parts = request.text.split(request.delimiter)

        return service_pb2.TextSplitResponse(num_parts=len(text_parts), parts=text_parts)

    def isprime(self, request_iterator, context):
        for req in request_iterator:
            yield service_pb2.IsPrimeResponse(number=req.number, isprime=_is_prime(req.number))

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ServiceServicer_to_server(Service(), server)
    server.add_insecure_port(f'127.0.0.1:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    try:
        serve(args.port)
    except KeyboardInterrupt:
        print('Shutting down')