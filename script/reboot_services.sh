#!/bin/bash --login

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

docker-compose -f docker-compose.prod.yml up -d --build