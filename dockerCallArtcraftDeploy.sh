#!/bin/sh

# example crontab entry for python via docker 
# 0 3 * * * /share/Container/artcraft/dockerCallArtcraftDeploy.sh >> /share/Container/artcraft/deploy.log 2>&1


# Artcraft Deployment Wrapper
docker run --rm \
  -v /share/Container/artcraft:/app \
  -v /share/data1/wwwroot:/var/www \
  python:3 \
  sh -c "pip install requests --quiet --root-user-action=ignore && python /app/deploy.py"

