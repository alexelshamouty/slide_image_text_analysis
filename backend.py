import grpc
from interfaces.process_presentation_pb2 import ProcessPresentationRequest, TaskStatusRequest
from interfaces.process_presentation_pb2_grpc import ProcessPresentationServiceStub
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PresentationClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = ProcessPresentationServiceStub(self.channel)
        self.response = None
        self.status = None
        self.result = None
        logger.info(f"Client initialized with server at {host}:{port}")

    def process_presentation(self, filepath: str, user_id: str):
        logger.info(f"Processing presentation", extra={
            'filepath': filepath,
            'user_id': user_id
        })
        try:
            request = ProcessPresentationRequest(filepath=filepath, user_id=user_id)
            self.response = self.stub.ProcessPresentation(request)
            logger.info("Successfully submitted presentation", extra={
                'task_id': self.response.task_id
            })
        except grpc.RpcError as e:
            logger.error("Failed to process presentation", extra={
                'error': str(e),
                'code': e.code()
            })
            raise
    
    def get_task_status(self):
        if not self.response:
            logger.error("No task has been submitted yet")
            return None, None
        
        logger.info("Checking task status", extra={
            'task_id': self.response.task_id
        })
        try:
            request = TaskStatusRequest(task_id=self.response.task_id)
            task_response = self.stub.GetTaskStatus(request)
            self.status = task_response.status
            self.result = task_response.result
            logger.debug("Retrieved task status", extra={
                'task_id': self.response.task_id,
                'status': self.status
            })
            return self.status, self.result
        except grpc.RpcError as e:
            logger.error("Failed to get task status", extra={
                'error': str(e),
                'code': e.code()
            })
            raise

if __name__ == '__main__':
    client = PresentationClient('localhost', 50051)
    client.process_presentation('/path/to/presentation', 'user123')
    status, result = client.get_task_status()
    logger.info("Task completed", extra={
        'status': status,
        'result': result
    })