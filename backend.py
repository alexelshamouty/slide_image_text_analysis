import grpc
from interfaces.process_presentation_pb2 import ProcessPresentationRequest, TaskStatusRequest, AllUserTasksRequest
from interfaces.process_presentation_pb2_grpc import ProcessPresentationServiceStub
import logging
from typing import Union, List
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
        logger.info(f"Processing presentation - filepath: {filepath}, user_id: {user_id}")
        try:
            request = ProcessPresentationRequest(filepath=filepath, user_id=user_id)
            self.response = self.stub.ProcessPresentation(request)
            logger.info(f"Successfully submitted presentation - task_id: {self.response.task_id}")
            return self.response
        except grpc.RpcError as e:
            logger.error(f"Failed to process presentation - error: {str(e)}, code: {e.code()}")
            raise
    
    @asyncify
    def get_task_status(self):
        if not self.response:
            logger.error("No task has been submitted yet - status: no_task")
            return None, None
        
        logger.info(f"Checking task status - task_id: {self.response.task_id}")
        try:
            request = TaskStatusRequest(task_id=self.response.task_id)
            task_response = self.stub.GetTaskStatus(request)
            self.status = task_response.status
            self.result = task_response.result
            logger.debug(f"Retrieved task status - task_id: {self.response.task_id}, status: {self.status}")
            return self.status, self.result
        except grpc.RpcError as e:
            logger.error(f"Failed to get task status - error: {str(e)}, code: {e.code()}")
            raise
    @asyncify
    def get_all_user_tasks(self, user_id: str):
        logger.info(f"Initiating request to retrieve all user tasks - user_id: {user_id}")
        try:
            request = AllUserTasksRequest(user_id=user_id)
            task_response = self.stub.GetAllUserTasks(request)
            results = task_response.tasks
            logger.info(f"Successfully retrieved all user tasks - user_id: {user_id}, tasks: {results}")
            return results
        # Assuming the response contains a list of tasks
        except grpc.RpcError as e:
            logger.error(f"Failed to retrieve all user tasks - error: {str(e)}, code: {e.code()}")
            raise


#Initialize the client
client = PresentationClient('application-grpc', 50051)

#Initialize the API server
app = FastAPI()
logger.info("API server initialized - service: fastapi")

@app.get("/get_all_user_tasks")
async def get_all_user_tasks(user_id: str):
    enteries = await client.get_all_user_tasks(user_id)
    logger.info(f"Retrieved all user tasks - user_id: {user_id}, tasks: {enteries}")
    return {
        "content": enteries
        }

@app.get("/get_task_status")
async def get_task_status(task_id: str):
    status, result = await client.get_task_status()
    return {
        "status": status,
        "result": result
    }
@app.post("/upload_presentation")
async def upload_presentation(user_id: str, files: List[UploadFile]):
    task_list = []
    file_names = []
    for file in files:
        logger.info(f"Received presentation upload - presentation: {file.filename}, user_id: {user_id}")
        # if not file.content_type.startswith('application/vnd.openxmlformats-officedocument.presentationml'):
        #     logger.error("Invalid file type", extra={
        #         'file_type': file.content_type
        #     })
        #     return {"error": "Invalid file type one pptx are supported"}

        #TODO
        # Make sure we have a mechanism to ensure that filename is sanitized
        async with aiofiles.open("/data/"+file.filename, 'wb') as out_file:
            while content := await file.read():
                await out_file.write(content)
        task_id = await client.process_presentation("/data/"+file.filename, user_id)
        file_names.append(file.filename)
        task_list.append(task_id.task_id)
    return {
        "filename": file_names,
        "task_id": task_list,
        "processing": True
    }
