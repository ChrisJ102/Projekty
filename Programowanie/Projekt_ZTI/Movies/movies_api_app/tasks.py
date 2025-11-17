from celery import shared_task
from movies_api_app.models import User
from celery.utils.log import get_task_logger
from time import sleep

logger = get_task_logger(__name__)


@shared_task
def longtime_add(x, y):
    logger.info('Got request - Starting work')
    sleep(4)
    logger.info('Work finished')
    return x+y


@shared_task
def askforuser(user_id: int):
    User.query.get_or_404(user_id)




