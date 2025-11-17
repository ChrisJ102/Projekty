from celery import shared_task
from movies_api_app.models import User


@shared_task
def divide(x, y):
    import time
    time.sleep(5)
    return x/y


@shared_task
def askforuser(user_id: int):
    user = User.query.get_or_404(user_id)
    return user.id
