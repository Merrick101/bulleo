web: gunicorn core.wsgi:application --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
worker: celery -A core worker --loglevel=info
beat: celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler