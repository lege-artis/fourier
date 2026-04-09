# kh-sim-log-service  --  KH-014
# Port: 8006  |  Runtime: Node.js 20 Alpine
#
# Build:  docker build -t kh-sim-log-service .
# Run:    docker run -p 8006:8006 \
#           -e MONGO_URI=mongodb://host.docker.internal:27017 \
#           kh-sim-log-service
# Health: curl http://localhost:8006/health

FROM node:20-alpine AS deps

WORKDIR /app
COPY package*.json ./
# Install production deps only
RUN npm ci --omit=dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM node:20-alpine

WORKDIR /app

# Non-root user for security
RUN addgroup -S kh && adduser -S kh -G kh
USER kh

COPY --from=deps --chown=kh:kh /app/node_modules ./node_modules
COPY --chown=kh:kh index.js smoke-test.js package.json ./

ENV PORT=8006 \
    NODE_ENV=production \
    LOG_LEVEL=info

EXPOSE 8006

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8006/health || exit 1

CMD ["node", "index.js"]
