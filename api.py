from celery import chain
from celery.result import AsyncResult
import redis
from tasks import (
    extract_content_task,
    process_images_task,
    analyze_content_task,
    save_analysis_task,
    app
)
from log_config import setup_logger

logger = setup_logger('analyzer.api')
results_redis = redis.Redis(host='results', port=6379, db=0)

def process_presentation(filepath: str, user_id: str):
    """
    Chain of tasks to process a presentation
    """
    result: AsyncResult = chain(
        extract_content_task.s(filepath, user_id),
        process_images_task.s(),
        analyze_content_task.s(),
        save_analysis_task.s()
    ).apply_async()

    try:
        results_redis.sadd(user_id, result.id)
    except Exception as exc:
        logger.error(f"Couldn't add the user id to results database for user {user_id}: {exc}")
    
    return result

def get_all_user_tasks(user_id: str):
    """
    Get all tasks for a user
    """
    logger.info(f"Starting cron job to update tasks - method: get_all_user_tasks")
    try:
        task_ids = results_redis.smembers(user_id)
        logger.info(f"Retrieved task IDs for user {user_id}: {task_ids}")
        tasks = [str(task_id).strip("b'").strip("'") for task_id in task_ids]
        task_results = []
        for task in tasks:
            try:
                task_result = app.AsyncResult(task).result
                if task_result is not None:
                    task_results.append(str(task_result))
                else:
                    task_results.append("Task status is not available")
            except Exception as exc:
                logger.error(f"Couldn't get task result for task {task}: {str(exc)}")
                task_results.append(str(exc))
        results = {task_id:task_result for task_id, task_result in zip(tasks, task_results)}
        return results
    except Exception as exc:
        logger.error(f"Couldn't get tasks for user {user_id}: {exc}")
        return {}
    
def get_task_status(task_id: str):
    """
    Get the status of a task
    """
    try:
        task = app.AsyncResult(task_id)
        logger.info(f"Retrieved task status for task {task_id}: {task.state}")
        return task.state, task.result
    except Exception as exc:
        logger.error(f"Couldn't get task status for task {task_id}: {exc}")
        return None, None
