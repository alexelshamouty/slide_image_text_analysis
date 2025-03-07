import grpc
from interfaces.process_presentation_pb2 import ProcessPresentationRequest, TaskStatusRequest, AllUserTasksRequest
from interfaces.process_presentation_pb2_grpc import ProcessPresentationServiceStub
import logging
from typing import Union
from fastapi import FastAPI, UploadFile, File
import aiofiles
import asyncio
from concurrent import futures
import functools
import json 
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def asyncify(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper

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
    
    @asyncify
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
    
    @asyncify
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
    @asyncify
    def get_all_user_tasks(self, user_id: str):
        logger.info("Initiating request to retrieve all user tasks", extra={
            'user_id': user_id
        })
        try:
            request = AllUserTasksRequest(user_id=user_id)
            task_response = self.stub.GetAllUserTasks(request)
            results = task_response.tasks
            logger.info("Successfully retrieved all user tasks", extra={
                'user_id': user_id,
                'tasks': results
            })
            return results
        # Assuming the response contains a list of tasks
        except grpc.RpcError as e:
            logger.error("Failed to retrieve all user tasks", extra={
                'error': str(e),
                'code': e.code()
            })
            raise


#Initialize the client
client = PresentationClient('localhost', 50051)

#Initialize the API server
app = FastAPI()
logger.info("API server initialized")

@app.get("/get_all_user_tasks")
async def get_all_user_tasks(user_id: str):
    return {"content": json.dumps(
            { 
            str(task):None if str(status).rstrip().lstrip() == None else str(status) 
            for entry in await client.get_all_user_tasks(user_id)
            for task, status in [entry.split(":")]
            }
        )
    }

@app.get("/get_task_status")
async def get_task_status(task_id: str):
    status, result = await client.get_task_status()
    return {
        "status": status,
        "result": result
    }
@app.post("/upload_presentation")
async def upload_presentation(user_id: str, file: UploadFile):
    logger.info("Received presentation upload", extra={
        'presentation': file.filename,
        'user_id': user_id
    })
    async with aiofiles.open(file.filename, 'wb') as out_file:
        while content := await file.read():
            await out_file.write(content)
    await client.process_presentation(file.filename, user_id)

    return {
        "filename": file.filename,
        "processing": True
    }
