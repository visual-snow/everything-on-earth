#!/bin/bash
set -e

echo "==================================="
echo "  Hospital Training Portal"
echo "  Trauma & Mass Casualty Triage"
echo "==================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null 2>&1; then
    echo "ERROR: Docker Compose is not available."
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

cd "$(dirname "$0")"

echo "[1/3] Starting all services..."
docker compose up -d --build

echo ""
echo "[2/3] Waiting for Ollama to be ready..."
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
    printf "."
done
echo " Ready."

echo ""
echo "[3/3] Pulling LLM model (first run only, ~4GB)..."
if ! docker exec training-ollama ollama list 2>/dev/null | grep -q "llama3"; then
    echo "Downloading llama3 model... this may take a while on first run."
    docker exec training-ollama ollama pull llama3
else
    echo "Model already cached. Skipping download."
fi

echo ""
echo "==================================="
echo "  Training Portal is running!"
echo ""
echo "  Portal:     http://localhost:8080"
echo "  Triage:     http://localhost:8080/triage/"
echo "  Sim:        http://localhost:8080/sim/"
echo "  Anatomy:    http://localhost:8080/anatomy/"
echo ""
echo "  To stop:    docker compose down"
echo "  To restart: ./start.sh"
echo "==================================="
