from concurrent import futures

import grpc
from celery.result import AsyncResult

from api import get_all_user_tasks, get_task_status, process_presentation
from interfaces import process_presentation_pb2, process_presentation_pb2_grpc
from log_config import setup_logger

# Configure logging
logger = setup_logger('analyzer.application')

#This is the gRPC server.
class PresentationServicer(process_presentation_pb2_grpc.ProcessPresentationServiceServicer):
    def ProcessPresentation(self, request, context):
        logger.info(f'Processing presentation request - filepath: {request.filepath}, user_id: {request.user_id}, peer: {context.peer()}')
        try:
            result = process_presentation(request.filepath, request.user_id)
            logger.info(f'Successfully initiated task - task_id: {result.id}, user_id: {request.user_id}')
            return process_presentation_pb2.ProcessPresentationResponse(
                task_id=result.id
            )
        except Exception as e:
            logger.error(f'Failed to process presentation - error: {str(e)}, user_id: {request.user_id}')
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal error occurred')
            raise

    def GetTaskStatus(self, request, context):
        logger.info(f'Checking task status - task_id: {request.task_id}, peer: {context.peer()}')
        try:
            task_state, task_result = get_task_status(request.task_id)
            logger.debug(f'Task status retrieved - task_id: {request.task_id}, status: {task_state}')
            return process_presentation_pb2.TaskStatusResponse(
                status=task_state,
                result=str(task_result) if task_result else ""
            )
        except Exception as e:
            logger.error(f'Failed to get task status - error: {str(e)}, task_id: {request.task_id}')
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to retrieve task status')
            raise
    def GetAllUserTasks(self, request, context):
        logger.info(f'Retrieving all tasks for user - user_id: {request.user_id}')
        try:
            result = get_all_user_tasks(request.user_id)
            logger.info(f'Successfully retrieved all user tasks - user_id: {request.user_id}, tasks: {result}')
            return process_presentation_pb2.AllUserTasksResponse(
                tasks=result
            )
        except Exception as e:
            logger.error(f'Failed to get all user tasks - error: {str(e)}, user_id: {request.user_id}')
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
    logger.info(f'gRPC task service is running on port 50051')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
