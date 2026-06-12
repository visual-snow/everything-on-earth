FROM node:20-slim AS frontend-build

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone Open Anatomy Explorer
RUN git clone --depth 1 https://github.com/biocat-ugent/Open-Anatomy-Explorer.git .

# Build frontend
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps && npm run build

# Find build output
RUN find /app/frontend -name "index.html" -not -path "*/node_modules/*" -not -path "*/src/*" | head -5

# Serve static frontend - Angular outputs to dist/<project-name>/
FROM nginx:alpine
COPY --from=frontend-build /app/frontend/docker/dist/ /usr/share/nginx/html/
EXPOSE 80
