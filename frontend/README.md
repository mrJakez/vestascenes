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

Security dependency updates are recorded in `package-lock.json`. Run
`npm audit` after updating and `node --test test/*.test.cjs` to check the
CommonJS compatibility copy of the upstream URI decoder security fix.
See `vendor/decode-uri-component/README.md` for its source and removal criteria.

Known remaining advisory: GHSA-vfj7-8cjw-p6xm (`braces`), pulled in by
`eslint-config-next -> @next/eslint-plugin-next -> fast-glob -> micromatch`.
As of 2026-10-16, no patched `braces` release exists and the latest Next.js
ESLint plugin still uses this dependency. npm reports five affected packages
for this one development dependency issue. Recheck upstream before removing it.

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
