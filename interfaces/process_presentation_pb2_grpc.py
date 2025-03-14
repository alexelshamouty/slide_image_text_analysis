# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import warnings

import grpc

from interfaces import \
    process_presentation_pb2 as interfaces_dot_process__presentation__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in interfaces/process_presentation_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ProcessPresentationServiceStub(object):
    """The service definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ProcessPresentation = channel.unary_unary(
                '/presentation.ProcessPresentationService/ProcessPresentation',
                request_serializer=interfaces_dot_process__presentation__pb2.ProcessPresentationRequest.SerializeToString,
                response_deserializer=interfaces_dot_process__presentation__pb2.ProcessPresentationResponse.FromString,
                _registered_method=True)
        self.GetTaskStatus = channel.unary_unary(
                '/presentation.ProcessPresentationService/GetTaskStatus',
                request_serializer=interfaces_dot_process__presentation__pb2.TaskStatusRequest.SerializeToString,
                response_deserializer=interfaces_dot_process__presentation__pb2.TaskStatusResponse.FromString,
                _registered_method=True)
        self.GetAllUserTasks = channel.unary_unary(
                '/presentation.ProcessPresentationService/GetAllUserTasks',
                request_serializer=interfaces_dot_process__presentation__pb2.AllUserTasksRequest.SerializeToString,
                response_deserializer=interfaces_dot_process__presentation__pb2.AllUserTasksResponse.FromString,
                _registered_method=True)


class ProcessPresentationServiceServicer(object):
    """The service definition
    """

    def ProcessPresentation(self, request, context):
        """Starts the processing chain
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTaskStatus(self, request, context):
        """Fetch the task status
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllUserTasks(self, request, context):
        """Get all users tasks
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ProcessPresentationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ProcessPresentation': grpc.unary_unary_rpc_method_handler(
                    servicer.ProcessPresentation,
                    request_deserializer=interfaces_dot_process__presentation__pb2.ProcessPresentationRequest.FromString,
                    response_serializer=interfaces_dot_process__presentation__pb2.ProcessPresentationResponse.SerializeToString,
            ),
            'GetTaskStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTaskStatus,
                    request_deserializer=interfaces_dot_process__presentation__pb2.TaskStatusRequest.FromString,
                    response_serializer=interfaces_dot_process__presentation__pb2.TaskStatusResponse.SerializeToString,
            ),
            'GetAllUserTasks': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllUserTasks,
                    request_deserializer=interfaces_dot_process__presentation__pb2.AllUserTasksRequest.FromString,
                    response_serializer=interfaces_dot_process__presentation__pb2.AllUserTasksResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'presentation.ProcessPresentationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('presentation.ProcessPresentationService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ProcessPresentationService(object):
    """The service definition
    """

    @staticmethod
    def ProcessPresentation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/presentation.ProcessPresentationService/ProcessPresentation',
            interfaces_dot_process__presentation__pb2.ProcessPresentationRequest.SerializeToString,
            interfaces_dot_process__presentation__pb2.ProcessPresentationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetTaskStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/presentation.ProcessPresentationService/GetTaskStatus',
            interfaces_dot_process__presentation__pb2.TaskStatusRequest.SerializeToString,
            interfaces_dot_process__presentation__pb2.TaskStatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetAllUserTasks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/presentation.ProcessPresentationService/GetAllUserTasks',
            interfaces_dot_process__presentation__pb2.AllUserTasksRequest.SerializeToString,
            interfaces_dot_process__presentation__pb2.AllUserTasksResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
