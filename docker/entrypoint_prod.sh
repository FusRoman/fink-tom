#!/bin/bash --login


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

docker-compose exec web conda run --no-capture-output -n fink_tom_env python manage.py collectstatic --no-input --clear
conda run -n fink_tom_env python manage.py readstreams

exec "$@"