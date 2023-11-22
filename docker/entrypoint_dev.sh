#!/bin/bash --login


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

path_root="Documents/Doctorat/fink-tom/"
path_manage="${path_root}fink_tom/manage.py"

conda run --no-capture-output -n fink_tom_env python $path_manage flush --no-input
conda run --no-capture-output -n fink_tom_env python $path_manage migrate
nohup conda run --no-capture-output -n fink_tom_env python $path_manage runserver 0.0.0.0:8000 &

exec "$@"