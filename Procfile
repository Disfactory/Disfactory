web: python3 ./manage.py migrate
web: cd backend && gunicorn -c gunicorn.conf.py gis_project.wsgi -b 0.0.0.0:80 > /srv/logs/web.log &
web: python3 ./manage.py qcluster &
