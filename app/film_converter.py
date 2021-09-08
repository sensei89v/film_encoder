from app.celery import celery_app
from app.db import get_session, create_new_film


@celery_app.task
def process_film(video_id):
    session = get_session()

    with session.begin():
        create_new_film(session, "TEST", "TEST")
