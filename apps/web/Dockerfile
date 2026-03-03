FROM oven/bun:1.3.10

WORKDIR /workspace

COPY package.json bunfig.toml turbo.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/ui/package.json packages/ui/package.json
COPY packages/api-client/package.json packages/api-client/package.json
COPY packages/config-eslint/package.json packages/config-eslint/package.json
COPY packages/config-ts/package.json packages/config-ts/package.json

RUN bun install

COPY apps/web ./apps/web
COPY packages ./packages

EXPOSE 5173

CMD ["bun", "run", "--cwd", "apps/web", "dev", "--host", "0.0.0.0", "--port", "5173"]
