# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import chord_pb2 as chord__pb2


class RegistryStub(object):
    """TODO: 1. verify whether the FindReply works as intended: the FindReply object can contain 2 or 3 fields as indicated in the assignment description
  TODO: 2. possibly optimize the classes structure: (after guaranteeing minimal functionality)

  the register service
  """

    def __init__(self, channel):
        """Constructor.

    Args:
      channel: A grpc.Channel.
    """
        self.register = channel.unary_unary(
            '/Registry/register',
            request_serializer=chord__pb2.RegisterRequest.SerializeToString,
            response_deserializer=chord__pb2.RegisterReply.FromString,
        )
        self.deregister = channel.unary_unary(
            '/Registry/deregister',
            request_serializer=chord__pb2.DeregisterRequest.SerializeToString,
            response_deserializer=chord__pb2.DeregisterReply.FromString,
        )
        self.populate_finger_table = channel.unary_unary(
            '/Registry/populate_finger_table',
            request_serializer=chord__pb2.PopulateRequest.SerializeToString,
            response_deserializer=chord__pb2.PopulateReply.FromString,
        )
        self.get_chord_info = channel.unary_unary(
            '/Registry/get_chord_info',
            request_serializer=chord__pb2.InfoRequest.SerializeToString,
            response_deserializer=chord__pb2.InfoReply.FromString,
        )


class RegistryServicer(object):
    """TODO: 1. verify whether the FindReply works as intended: the FindReply object can contain 2 or 3 fields as indicated in the assignment description
  TODO: 2. possibly optimize the classes structure: (after guaranteeing minimal functionality)

  the register service
  """

    def register(self, request, context):
        """called ONLY by Node objects
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def deregister(self, request, context):
        """called ONLY by Node objects
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def populate_finger_table(self, request, context):
        """called ONLY by Node objects
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_chord_info(self, request, context):
        """called ONLY BY CLIENT
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RegistryServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'register': grpc.unary_unary_rpc_method_handler(
            servicer.register,
            request_deserializer=chord__pb2.RegisterRequest.FromString,
            response_serializer=chord__pb2.RegisterReply.SerializeToString,
        ),
        'deregister': grpc.unary_unary_rpc_method_handler(
            servicer.deregister,
            request_deserializer=chord__pb2.DeregisterRequest.FromString,
            response_serializer=chord__pb2.DeregisterReply.SerializeToString,
        ),
        'populate_finger_table': grpc.unary_unary_rpc_method_handler(
            servicer.populate_finger_table,
            request_deserializer=chord__pb2.PopulateRequest.FromString,
            response_serializer=chord__pb2.PopulateReply.SerializeToString,
        ),
        'get_chord_info': grpc.unary_unary_rpc_method_handler(
            servicer.get_chord_info,
            request_deserializer=chord__pb2.InfoRequest.FromString,
            response_serializer=chord__pb2.InfoReply.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'Registry', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


class NodeStub(object):
    """//////////////////////////////////////////////////////////////////////////////////////////////////////////

  the node service
  """

    def __init__(self, channel):
        """Constructor.

    Args:
      channel: A grpc.Channel.
    """
        self.get_finger_table = channel.unary_unary(
            '/Node/get_finger_table',
            request_serializer=chord__pb2.InfoRequest.SerializeToString,
            response_deserializer=chord__pb2.InfoReply.FromString,
        )
        self.save_key = channel.unary_unary(
            '/Node/save_key',
            request_serializer=chord__pb2.SaveRequest.SerializeToString,
            response_deserializer=chord__pb2.SaveReply.FromString,
        )
        self.remove_key = channel.unary_unary(
            '/Node/remove_key',
            request_serializer=chord__pb2.RemoveRequest.SerializeToString,
            response_deserializer=chord__pb2.RemoveReply.FromString,
        )
        self.find_key = channel.unary_unary(
            '/Node/find_key',
            request_serializer=chord__pb2.FindRequest.SerializeToString,
            response_deserializer=chord__pb2.FindReply.FromString,
        )
        self.quit = channel.unary_unary(
            '/Node/quit',
            request_serializer=chord__pb2.QuitRequest.SerializeToString,
            response_deserializer=chord__pb2.QuitReply.FromString,
        )


class NodeServicer(object):
    """//////////////////////////////////////////////////////////////////////////////////////////////////////////

  the node service
  """

    def get_finger_table(self, request, context):
        """the same classes used by the Registry are used by the Node as they have the same fields

    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def save_key(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def remove_key(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def find_key(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def quit(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'get_finger_table': grpc.unary_unary_rpc_method_handler(
            servicer.get_finger_table,
            request_deserializer=chord__pb2.InfoRequest.FromString,
            response_serializer=chord__pb2.InfoReply.SerializeToString,
        ),
        'save_key': grpc.unary_unary_rpc_method_handler(
            servicer.save_key,
            request_deserializer=chord__pb2.SaveRequest.FromString,
            response_serializer=chord__pb2.SaveReply.SerializeToString,
        ),
        'remove_key': grpc.unary_unary_rpc_method_handler(
            servicer.remove_key,
            request_deserializer=chord__pb2.RemoveRequest.FromString,
            response_serializer=chord__pb2.RemoveReply.SerializeToString,
        ),
        'find_key': grpc.unary_unary_rpc_method_handler(
            servicer.find_key,
            request_deserializer=chord__pb2.FindRequest.FromString,
            response_serializer=chord__pb2.FindReply.SerializeToString,
        ),
        'quit': grpc.unary_unary_rpc_method_handler(
            servicer.quit,
            request_deserializer=chord__pb2.QuitRequest.FromString,
            response_serializer=chord__pb2.QuitReply.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'Node', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
