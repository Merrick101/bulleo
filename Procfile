web: gunicorn core.wsgi
worker: celery -A core worker --loglevel=info
beat: celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler