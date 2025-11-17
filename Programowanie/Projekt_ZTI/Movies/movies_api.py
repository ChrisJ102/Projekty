from movies_api_app import create_app, ext_celery


app = create_app()
app.app_context().push()
celery = ext_celery.celery

