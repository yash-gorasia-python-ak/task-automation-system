from celery import Celery
from app.core.config import settings
from kombu import Queue, Exchange
from app.core.config import settings

celery_app = Celery(
    "app_worker", broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL
)


celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("send_reminder", Exchange("send_reminder"), routing_key="send_reminder"),
    Queue("system_check", Exchange("system_check"), routing_key="system_check"),
    Queue("send_comic", Exchange("send_comic"), routing_key="send_comic"),
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# Route tasks automatically by name
celery_app.conf.task_routes = {
    "reminder": {"queue": "send_reminder"},
    "system_check": {"queue": "system_check"},
    "send_comic": {"queue": "send_comic"},
}


celery_app.conf.update(
    beat_scheduler="sqlalchemy_celery_beat.schedulers:DatabaseScheduler",
    beat_dburi=f"{settings.CELERY_DB_URL}",
    beat_schema="celery_schema",
    worker_pool="prefork",
    task_track_started=True,
)

celery_app.autodiscover_tasks(["app.queue.tasks"])


celery_app.conf.timezone = "UTC"
