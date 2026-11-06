# Topiome web image. Build from the repository root:
#   docker build -f infra/docker/web.Dockerfile --build-arg API_URL=http://api:8000 -t topiome-web .
FROM node:22-alpine AS deps
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web ./
# Next.js bakes the /api rewrite target in at build time.
ARG API_URL=http://api:8000
ENV API_URL=$API_URL \
    NEXT_OUTPUT=standalone \
    NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1
RUN addgroup -S topiome && adduser -S topiome -G topiome
COPY --from=build --chown=topiome:topiome /app/.next/standalone ./
COPY --from=build --chown=topiome:topiome /app/.next/static ./.next/static
USER topiome
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD wget -qO- http://127.0.0.1:3000/ >/dev/null || exit 1
CMD ["node", "server.js"]
