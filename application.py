import grpc
from concurrent import futures
from celery.result import AsyncResult
from interfaces import process_presentation_pb2_grpc, process_presentation_pb2
from tasks import process_presentation,get_all_user_tasks,get_task_status
from log_config import setup_logger
from concurrent import futures
# Configure logging
logger = setup_logger('analyzer.application')

#This is the gRPC server.
class PresentationServicer(process_presentation_pb2_grpc.ProcessPresentationServiceServicer):
    def ProcessPresentation(self, request, context):
        logger.info('Processing presentation request', extra={
            'filepath': request.filepath,
            'user_id': request.user_id,
            'peer': context.peer()
        })
        try:
            result = process_presentation(request.filepath, request.user_id)
            logger.info('Successfully initiated task', extra={
                'task_id': result.id,
                'user_id': request.user_id
            })
            return process_presentation_pb2.ProcessPresentationResponse(
                task_id=result.id
            )
        except Exception as e:
            logger.error('Failed to process presentation', extra={
                'error': str(e),
                'user_id': request.user_id
            })
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal error occurred')
            raise

    def GetTaskStatus(self, request, context):
        logger.info('Checking task status', extra={
            'task_id': request.task_id,
            'peer': context.peer()
        })
        try:
            task_state, task_result = get_task_status(request.task_id)
            logger.debug('Task status retrieved', extra={
                'task_id': request.task_id,
                'status': task_state
            })
            return process_presentation_pb2.TaskStatusResponse(
                status=task_state,
                result=str(task_result) if task_result else ""
            )
        except Exception as e:
            logger.error('Failed to get task status', extra={
                'error': str(e),
                'task_id': request.task_id
            })
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to retrieve task status')
            raise
    def GetAllUserTasks(self, request, context):
        logger.info('Retrieving all tasks for user', extra={
            'user_id': request.user_id,
        })

        try:
            result = get_all_user_tasks(request.user_id)
            logger.info('Successfully retrieved all user tasks', extra={
                'user_id': request.user_id,
                'tasks': result
            })
            return process_presentation_pb2.AllUserTasksResponse(
                tasks=result
            )
        except Exception as e:
            logger.error('Failed to all user tasks tasks', extra={
                'error': str(e),
                'user_id': request.user_id
            })
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to retrieve tasks')
            raise

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    process_presentation_pb2_grpc.add_ProcessPresentationServiceServicer_to_server(
        PresentationServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('gRPC task service is running on port 50051')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
