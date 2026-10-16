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

The App Router uses React 19. `@vestaboard/installables` still declares React 18
peer dependencies, so `package.json` overrides those peers with the app's React
and React DOM versions. Keep this targeted override until the library supports
React 19, and commit `package-lock.json` whenever dependencies change so Docker's
`npm ci` uses the same dependency tree.

Vestaboard imports access `window` at module load time. Load views that import
this library with `next/dynamic` and `ssr: false` from a client component.

First, run the development server:

```bash
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
