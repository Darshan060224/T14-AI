#!/bin/bash
# ═══════════════════════════════════════════════
# T14 AI — Start All Services
# ═══════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

# Navigate to project root (where this script lives)
cd "$(dirname "$0")"

echo ""
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}  🛡️  T14 AI — SOC Analyst Assistant${NC}"
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════${NC}"
echo ""

# ── Check Docker ──────────────────────────────
echo -e "${YELLOW}[1/5]${NC} Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running. Start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# ── Check Docker Compose ─────────────────────
echo -e "${YELLOW}[2/5]${NC} Checking Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose available${NC}"

# ── Copy .env if needed ──────────────────────
echo -e "${YELLOW}[3/5]${NC} Checking environment..."
if [ ! -f .env ]; then
    echo -e "  Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}  ✓ .env created${NC}"
else
    echo -e "${GREEN}✓ .env exists${NC}"
fi

# ── Build and Start Containers ───────────────
echo ""
echo -e "${YELLOW}[4/5]${NC} Starting all services (FastAPI + Ollama + ChromaDB)..."
echo -e "  This may take a few minutes on first run..."
echo ""

docker compose up --build -d

echo ""

# ── Pull Qwen3 Model ────────────────────────
echo -e "${YELLOW}[5/5]${NC} Ensuring Qwen3 8B model is available..."

echo "  Checking if native Ollama is running..."
if ! curl -sf http://localhost:11434/api/tags > /dev/null; then
    echo "  Starting Ollama locally in the background..."
    ollama serve > ollama.log 2>&1 &
    sleep 3
fi

if ollama list 2>/dev/null | grep -q "qwen3:8b"; then
    echo -e "${GREEN}✓ Qwen3 8B model already available${NC}"
else
    echo -e "  Pulling Qwen3 8B model (~5GB, first time only)..."
    ollama pull qwen3:8b
    echo -e "${GREEN}✓ Qwen3 8B model pulled${NC}"
fi

# ── Wait for FastAPI ─────────────────────────
echo ""
echo -e "  Waiting for FastAPI to be ready..."
for i in $(seq 1 60); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    sleep 2
done

# ── Final Status ─────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════${NC}"

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}${BOLD}  ✅ T14 AI is running!${NC}"
    echo ""
    echo -e "  ${BOLD}Web UI:${NC}       http://localhost:8000"
    echo -e "  ${BOLD}Swagger UI:${NC}   http://localhost:8000/docs"
    echo -e "  ${BOLD}ReDoc:${NC}        http://localhost:8000/redoc"
    echo -e "  ${BOLD}Health:${NC}       http://localhost:8000/health"
    echo ""
    echo -e "  ${BOLD}Health Status:${NC} ${HEALTH}"
else
    echo -e "${YELLOW}${BOLD}  ⏳ Services starting up...${NC}"
    echo ""
    echo -e "  FastAPI is still loading (embedding model + knowledge base)."
    echo -e "  Check status: ${BOLD}curl http://localhost:8000/health${NC}"
    echo -e "  View logs:    ${BOLD}docker compose logs -f app${NC}"
fi

echo ""
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════${NC}"
echo -e "  Stop:     ${BOLD}docker compose down${NC}"
echo -e "  Logs:     ${BOLD}docker compose logs -f${NC}"
echo -e "  Restart:  ${BOLD}docker compose restart${NC}"
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════${NC}"
echo ""
