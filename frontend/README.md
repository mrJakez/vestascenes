Vestaboard editor

## Deploy

docker-compose.yml

```yaml
services:
  vestaboard-editor-frontend:
    image: ghcr.io/kacpak/vestaboard-editor:latest
    environment:
      - BACKEND_URL=http://example.com
    ports:
      - "3000:3000"
```

## How to contribute

First, run the development server:

```bash
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
