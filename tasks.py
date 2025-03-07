import os
from celery import Celery, chain
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
from celery.schedules import crontab
import logging
import redis
from PIL import Image
from load_and_generate import (
    extract_content_from_slides,
    process_images,
    split_text,
    process_text_with_images,
)
from typing import List, Dict
from log_config import setup_logger
from datetime import datetime


# Configure Celery
app = Celery('tasks', 
             broker='redis://broker:6379/0',
             backend='redis://backend:6379/0')

app.conf.result_backend = 'redis://backend:6379/0'

app.conf.update(
    worker_concurrency=10,
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC'
)

app.conf.beat_schedule = {
    'update_tasks': {
        'task': 'tasks.update_tasks',
        'schedule': crontab(hour=0, minute=0, day_of_week = '*'),
    },
    'crawler': {
        'task': 'tasks.crawl',
        'schedule': crontab(minute='*/1'),
    },
}

# Configure logging
logger = setup_logger('analyzer.tasks')
results_redis = redis.Redis(host='results', port=6379, db=0)
logger.info("Clients setup successfully")

@app.on_after_configure.connect
def iniaite_logging(sender, **kwargs):
    global logger 
    if not logger:
        logger = setup_logger('analyzer.tasks')
    global results_redis
    if not results_redis:
        results_redis = redis.Redis(host='results', port=6379, db=0)
    logger.info("Celery configured successfully")

@app.task(bind=True, max_retries=3, name='tasks.extract_content')
def extract_content_task(self, filepath: str, user_id: str):
    """Extract content from PowerPoint file"""
    try:
        logger.info(f"Extracting content from {filepath} for user {user_id}")
        text, images = extract_content_from_slides(filepath)
        # Save images temporarily
        filename = os.path.basename(filepath).split(".")[0]
        image_paths = []
        for i, img in enumerate(images):
            path = f"/data/{filename}_{i}.png"
            img.save(path)
            image_paths.append(path)
        return {'text': text, 'image_paths': image_paths, 'filepath': filepath, 'user_id': user_id}
    except Exception as exc:
        logger.error(f"Error extracting content from {filepath}: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.process_images')
def process_images_task(self, content_dict: Dict):
    """Process images and generate descriptions"""
    try:
        images = [Image.open(path) for path in content_dict['image_paths']]
        descriptions = process_images(images)
        # Clean up temporary image files
        for path in content_dict['image_paths']:
            os.remove(path)
        return {'text': content_dict['text'], 'descriptions': descriptions, 
                'filepath': content_dict['filepath'], 'user_id': content_dict['user_id']}
    except Exception as exc:
        logger.error(f"Error processing images for user {content_dict.get('user_id')}: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.analyze_content')
def analyze_content_task(self, process_dict: Dict):
    """Analyze text and image descriptions"""
    try:
        chunks = split_text(process_dict['text'])
        analysis = process_text_with_images(chunks, process_dict['descriptions'])
        return {'content': analysis['content'], 'filepath': process_dict['filepath'], 
                'user_id': process_dict['user_id']}
    except Exception as exc:
        logger.error(f"Error analyzing content for user {process_dict.get('user_id')}: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3, name='tasks.save_analysis')
def save_analysis_task(self, analysis_dict: Dict):
    """Save analysis results"""
    try:
        filename = analysis_dict['filepath']
        output_path = f"{filename}_analysis.txt"
        with open(output_path, "a+") as f:
            f.write("\n")
            f.write(analysis_dict['content'])
        return output_path
    except Exception as exc:
        logger.error(f"Error saving analysis for user {analysis_dict.get('user_id')}: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, name='tasks.update_tasks')
def update_tasks(self):
    """Update the status of tasks in the results database"""
    try:
        # Get all task IDs from the results database
        user_ids = results_redis.keys('*')
        task_results = {key: results_redis.smembers(key) for key in user_ids}
        for user_id, task_ids in task_results.items():
            logger.info(f"Updating tasks for user {user_id}")
            for task_id in task_ids:
                task_id = task_id.decode('utf-8')
                task = app.AsyncResult(task_id)
                if task.state == 'SUCCESS':
                    # Remove the task ID from the results database
                    results_redis.srem(user_id, task_id)
        logger.info("User tasks database updated successfully")
    except Exception as exc:
        logger.error(f"Error updating tasks: {exc}")

@app.task(bind=True, name='tasks.crawl')
def crawl(self):
    """ This is just a dummy task """
    logger.info(f"Crawling -- ${datetime.utcnow()}")