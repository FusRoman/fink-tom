# fink-tom

### DEV mode

build docker dev image using docker-compose
```bash
docker-compose build
```

run the container
```bash 
docker-compose up -d
```

make django migration
don't forget to run migration of there is any modification on the database
```bash
docker-compose exec web conda run --no-capture-output -n fink_tom_env python manage.py migrate
```

access to the TOM database
```bash
docker-compose exec db psql --username=fink_tom_default --dbname=fink_tom_dev
```

create a new user in dev mode
```bash
docker-compose exec web conda run --no-capture-output -n fink_tom_env python fink_tom/manage.py createsuperuser
```

### Prod mode

build and up the production containers
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

collect static files
```bash
docker-compose exec web conda run --no-capture-output -n fink_tom_env python manage.py collectstatic --no-input --clear
```