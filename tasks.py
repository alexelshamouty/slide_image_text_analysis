import os
from celery import Celery, chain
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
import logging
from PIL import Image
from load_and_generate import (
    extract_content_from_slides,
    process_images,
    split_text,
    process_text_with_images,
)
from typing import List, Dict
import grpc
from interfaces import process_presentation_pb2_grpc, process_presentation_pb2

from concurrent import futures

# Configure Celery
app = Celery('tasks', 
             broker='redis://broker:6379/0',
             backend='redis://backend:6379/0')
app.conf.update(
    worker_concurrency=10,
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC'
)

# Configure logging
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)

@app.task(bind=True, max_retries=3, name='tasks.extract_content')
def extract_content_task(self, filepath: str, user_id: str):
    """Extract content from PowerPoint file"""
    try:
        text, images = extract_content_from_slides(filepath)
        self.request = user_id
        # Save images temporarily
        filename = os.path.basename(filepath).split(".")[0]
        image_paths = []
        for i, img in enumerate(images):
            path = f"{filename}_{i}.png"
            img.save(path)
            image_paths.append(path)
        return {'text': text, 'image_paths': image_paths, 'filepath': filepath, 'user_id': user_id}
    except Exception as exc:
        logger.error(f"Error extracting content: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.process_images')
def process_images_task(self, content_dict: Dict):
    """Process images and generate descriptions"""
    try:
        self.request = content_dict['user_id']
        images = [Image.open(path) for path in content_dict['image_paths']]
        descriptions = process_images(images)
        # Clean up temporary image files
        for path in content_dict['image_paths']:
            os.remove(path)
        return {'text': content_dict['text'], 'descriptions': descriptions, 
                'filepath': content_dict['filepath'], 'user_id': content_dict['user_id']}
    except Exception as exc:
        logger.error(f"Error processing images: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.analyze_content')
def analyze_content_task(self, process_dict: Dict):
    """Analyze text and image descriptions"""
    try:
        chunks = split_text(process_dict['text'])
        self.request = process_dict['user_id']
        analysis = process_text_with_images(chunks, process_dict['descriptions'])
        return {'content': analysis['content'], 'filepath': process_dict['filepath'], 
                'user_id': process_dict['user_id']}
    except Exception as exc:
        logger.error(f"Error analyzing content: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.save_analysis')
def save_analysis_task(self, analysis_dict: Dict):
    """Save analysis results"""
    try:
        filename = os.path.basename(analysis_dict['filepath']).split(".")[0]
        self.request = analysis_dict['user_id']
        output_path = f"{filename}_analysis.txt"
        with open(output_path, "a+") as f:
            f.write("\n")
            f.write(analysis_dict['content'])
        return output_path
    except Exception as exc:
        logger.error(f"Error saving analysis: {exc}")
        raise self.retry(exc=exc, countdown=60)

def process_presentation(filepath: str, user_id: str):
    """
    Chain of tasks to process a presentation
    """
    return chain(
        extract_content_task.s(filepath, user_id),
        process_images_task.s(),
        analyze_content_task.s(),
        save_analysis_task.s()
    ).apply_async()