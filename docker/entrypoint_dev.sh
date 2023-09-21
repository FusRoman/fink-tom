#!/bin/bash --login


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py flush --no-input
conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py migrate
nohup conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py runserver 0.0.0.0:8000 &

exec "$@"