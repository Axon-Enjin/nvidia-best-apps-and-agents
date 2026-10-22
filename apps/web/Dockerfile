# Next.js frontend for Sentinel Claims. Build from the repository root:
#   docker build -f apps/web/Dockerfile .
# Prepared alongside compose.yaml; no image has been built on the development host yet.
FROM node:24.22.1-trixie-slim AS build
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
RUN npm install --global pnpm@11.10.0
COPY apps/web/package.json apps/web/pnpm-lock.yaml apps/web/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY apps/web/ ./
RUN pnpm build && pnpm prune --prod

FROM node:24.22.1-trixie-slim
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=build --chown=node:node /app/package.json /app/next.config.ts ./
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/.next ./.next
USER node
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "start", "-H", "0.0.0.0", "-p", "3000"]
