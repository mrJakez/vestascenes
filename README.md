## vesta-control 🚀

This is a vestaboard server implementation which organizes the vestaboard (http://vestaboard.com) related content within scenes.

This helps to priotize the content which you are interested in. The implementation contains scenes for ChatGPT
requests, Strava-Stats and some other random content generating scenes.


### Key concept
The key concept behind the app are scenes which are executed by a Director on a regular basis. Each scene anounces with its priority response how importent the current scene content is.
This information will be taken by the Director into account to calculate which scene is next.




### Container Setup
The application is orchestrated by docker compose and is currently organized in two main applications:
#### API
Contain the business logic of vesta-control.
#### Runner
The runner is a container with one python application which is triggering the http://api/execute endpoint every 15 seconds. Thanks to this the application logic resists within the api container and is triggered periodically within the given interval.


## Cheat Sheet

### Debugging / deploy tips:
```bash
# Manual start on Mac:
sudo docker-compose up --build -d

# get all log statements of running containers
docker-compose logs -f

# check which containers are up and running
sudo docker-compose watch

# log interactively into container
docker exec -ti vesta-control-api-1 /bin/sh

########## fetch new sources from git and rebuild ##########
# stop current project in container manager!
cd /volume1/docker/vestaboardControl/
git pull origin main
sudo docker-compose up --build --force-recreate --no-start
# start in container manager :)
```

### Vestaboard Markup Language Example
```json
{
  "props": {
    "title": "ruhrtour 2019",
    "distance": "182km",
    "avg": "25kmh"
  },
  "components": [
    {
      "template": "{63}{63}      Strava      {63}{63}",
      "style": {
        "height": 1,
        "justify": "center"
      }
    },
    {
      "template": "{63}",
      "style": {
        "height": 1,
        "width": 1,
        "justify": "left"
      }
    },
    {
      "template": "{{title}}",
      "style": {
        "height": 1,
        "width": 20,
        "justify": "center"
      }
    },
    {
      "template": "{63}",
      "style": {
        "height": 1,
        "width": 1,
        "justify": "left"
      }
    },
    {
      "template": "dist ",
      "style": {
        "height": 1,
        "width": 5,
        "justify": "left"
      }
    },
    {
      "template": "{{distance}}",
      "style": {
        "height": 1,
        "width": 5,
        "justify": "left"
      }
    }
  ]
}
```