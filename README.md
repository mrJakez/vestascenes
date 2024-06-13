## Cheat Sheet


// Manual start on Mac:
sudo docker-compose up --build -d

// log verbose whole running compose services
docker-compose logs -f

// stop the magic
udo docker-compose watch

// log interactively into container
docker exec -ti vestaboard_control-runner-1 /bin/sh


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