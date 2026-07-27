from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "hospital",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks"],   
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery.conf.beat_schedule = {
    "send-daily-appointment-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "send-monthly-activity-reports": {
    "task":     "tasks.send_monthly_report",
    "schedule": crontab(hour=6, minute=0, day_of_month=1),
}
}



