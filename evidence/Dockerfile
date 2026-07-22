# Multi-stage: build the Evidence static site, then serve it with nginx.
FROM node:20-slim AS build
WORKDIR /app
COPY evidence/package.json evidence/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY evidence/ ./
# boreas.duckdb is mounted at /data/boreas.duckdb at build time via bind mount.
ENV EVIDENCE_SOURCE__boreas__filename=/data/boreas.duckdb
RUN --mount=type=bind,source=boreas.duckdb,target=/data/boreas.duckdb,ro \
    npm run sources && npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
