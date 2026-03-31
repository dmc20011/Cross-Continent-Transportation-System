set -e

docker compose down
yes | docker container prune
yes | docker volume prune -a
docker compose build
docker compose up
