## Cheat Sheet


// Manual start on Mac:
sudo docker-compose up --build -d

// log verbose whole running compose services
docker-compose logs -f

// stop the magic
udo docker-compose watch

// log interactively into container
docker exec -ti vestaboard_control-runner-1 /bin/sh  