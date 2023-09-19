#!/bin/bash --login

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -aq)
docker volume rm $(docker volume ls -q)
docker system prune --all -f

docker-compose -f docker-compose.prod.yml up -d --build