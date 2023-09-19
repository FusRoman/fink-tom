#!/bin/bash --login


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

conda run --no-capture-output -n fink_tom_env python manage.py migrate
conda run --no-capture-output -n fink_tom_env python manage.py collectstatic --no-input --clear
nohup conda run -n fink_tom_env python manage.py readstreams > readstreams.log 2>&1 &

exec "$@"