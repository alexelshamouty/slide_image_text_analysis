import grpc
from concurrent import futures
from celery.result import AsyncResult
from interfaces import process_presentation_pb2_grpc, process_presentation_pb2
from tasks import process_presentation

class PresentationServicer(process_presentation_pb2_grpc.ProcessPresentationServiceServicer):
    def ProcessPresentation(self, request, context):
        result = process_presentation(request.filepath, request.user_id)
        return process_presentation_pb2.ProcessPresentationResponse(
            task_id=result.id
        )

    def GetTaskStatus(self, request, context):
        task_result = AsyncResult(request.task_id)
        return process_presentation_pb2.TaskStatusResponse(
            status=task_result.status,
            result=str(task_result.result) if task_result.result else ""
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    process_presentation_pb2_grpc.add_ProcessPresentationServiceServicer_to_server(
        PresentationServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC task service is running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
