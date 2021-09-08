from celery import Celery

CELERY_IMPORTS = ("app.film_converter", )

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379',
    include=CELERY_IMPORTS
)

