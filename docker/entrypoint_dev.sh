#!/bin/bash --login

conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py flush --no-input
conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py migrate

exec "$@"