web: gunicorn core.wsgi:application --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
workerbeat: honcho start -f Procfile.workerbeat
