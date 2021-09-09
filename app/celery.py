from celery import Celery
from app.config import load_config

CELERY_IMPORTS = ("app.film_converter", )
_config = load_config()

celery_app = Celery(
    'tasks',
    broker=_config['celery_broker_url'],
    include=CELERY_IMPORTS
)
