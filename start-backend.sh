#!/bin/bash
# ═══════════════════════════════════════════════
# Start FastAPI Backend & ChromaDB
# ═══════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

echo -e "\033[0;36m\033[1mStarting Backend Services (ChromaDB + FastAPI)...\033[0m"

# Ensure environment file exists
if [ ! -f .env ]; then
    cp .env.example .env
fi



# Start ChromaDB in the background
echo "Starting ChromaDB Vector Store..."
docker compose up -d chromadb

echo "Building and starting FastAPI app..."
# Start FastAPI app and attach logs to this terminal
docker compose up --build app
