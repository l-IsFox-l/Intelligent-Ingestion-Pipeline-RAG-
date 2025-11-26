# Celery options
import os
from celery import Celery
from app.core.config import settings

celery_app = Celery("worker")

redis_url = f"redis://{settings.REDIS_HOST}:6379/0"

celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    # serialization format
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    imports=["app.worker.tasks"],
    broker_connection_retry_on_startup=True,
)