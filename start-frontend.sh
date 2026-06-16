#!/bin/bash
# ═══════════════════════════════════════════════
# Start Frontend Web UI
# ═══════════════════════════════════════════════

set -e
cd "$(dirname "$0")/frontend"

echo -e "\033[0;36m\033[1mStarting Frontend Web UI...\033[0m"
echo -e "\033[0;32m\033[1m✅ Web Interface available at: http://localhost:8080\033[0m"
echo -e "\033[1;33mEnsure that the backend is running separately via start-backend.sh\033[0m"
echo ""

# Run a simple HTTP server to serve the static frontend files
python3 -m http.server 8080
