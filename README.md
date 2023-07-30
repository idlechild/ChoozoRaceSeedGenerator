# ChoozoRaceSeedGenerator

docker build --tag choozo . \
docker run -e CHOOZO_TOKEN=%CHOOZO_TOKEN% -e SMR_RACETIME_CLIENT_ID=%SMR_RACETIME_CLIENT_ID% -e SMR_RACETIME_CLIENT_SECRET=%SMR_RACETIME_CLIENT_SECRET% -d choozo

docker stop <container_name> \
docker rm <container_name>

docker system prune -a \
docker system df

