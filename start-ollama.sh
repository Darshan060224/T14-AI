#!/bin/bash
# ═══════════════════════════════════════════════
# Start Ollama LLM Service
# ═══════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

echo -e "\033[0;36m\033[1mStarting Native Ollama (Qwen3:8B)...\033[0m"

if ! command -v ollama &> /dev/null; then
    echo -e "\033[0;31m✗ Ollama not found on host. Please install Ollama from https://ollama.com/\033[0m"
    exit 1
fi

echo "Checking if native Ollama is running..."
if ! curl -sf http://localhost:11434/api/tags > /dev/null; then
    echo "Starting Ollama locally in the background..."
    ollama serve > ollama.log 2>&1 &
    sleep 3
fi

# Pull the model if missing
echo "Ensuring Qwen3:8B model is loaded (this may take time if downloading)..."
ollama pull qwen3:8b

echo -e "\033[0;32m\033[1m✅ Ollama is ready on http://localhost:11434\033[0m"
echo ""
echo "Ollama is running natively in the background."
