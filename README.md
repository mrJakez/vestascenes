## vesta-control 🚀

This is a vestaboard server implementation which organizes the vestaboard (http://vestaboard.com) related content within scenes.

This helps to prioritize the content which you are interested in. The implementation contains scenes for ChatGPT
requests, Strava-Stats and some other random content generating scenes.


### Key concept
The key concept behind the app are scenes which are executed by a Director on a regular basis. Each scene announces with its priority response how important the current scene content is.
This information will be taken by the Director into account to calculate which scene is next.




### Container Setup
The application is orchestrated by docker compose and is currently organized in two main applications:
#### API
Contain the business logic of vesta-control.
#### Runner
The runner is a container with one python application which is triggering the http://api/execute endpoint every 15 seconds. Thanks to this the application logic resists within the api container and is triggered periodically within the given interval.



### TODOS
- Space Launch Alerts => Display when a SpaceX liftoff happens
- improve chatgpt quote format
- runner should just trigger /execute when api is initialized
- optimize init-snapshots performance

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
docker exec -ti vestaboard-api-1 /bin/sh

########## fetch new sources from git and rebuild ##########
# stop current project in container manager!
cd /volume1/docker/vestaboard/

# remove local git changes (if required)
git restore .

# refresh rom git
git pull origin main

# rebuild the container:
sudo docker-compose build --no-cache api

# trigger "Aktion -> Bereinigen" of the project
# trigger "Aktion -> Erstellen" of the project
```

### Character Codes
https://docs.vestaboard.com/docs/characterCodes

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