# T14 AI — RAG-Powered SOC Analyst & Security Assistant

> AI-Powered SOC Analyst Assistant using FastAPI, Qwen3 8B (Ollama), and RAG with ChromaDB

[![CI/CD](https://github.com/YOUR_USERNAME/t14-ai-security-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/t14-ai-security-assistant/actions)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

**T14 AI** is an AI-powered cybersecurity assistant designed for Security Operations Center (SOC) analysts. It leverages **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware security guidance by combining a local LLM (Qwen3 8B via Ollama) with a curated cybersecurity knowledge base.

### Problem Statement

Security analysts spend significant time:
- Investigating alerts and understanding log events
- Mapping attacks to MITRE ATT&CK framework
- Writing incident summaries for stakeholders
- Looking up detection rules and mitigation strategies

**T14 AI automates these tasks** using an LLM enhanced with a cybersecurity knowledge base containing MITRE ATT&CK techniques, Sigma detection rules, OWASP guidelines, and incident response playbooks.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔒 **Security Chat (RAG)** | Ask cybersecurity questions with knowledge-base-backed answers |
| 📊 **Log Analysis** | Analyze security logs with MITRE ATT&CK mapping |
| 🎯 **MITRE ATT&CK Mapping** | Auto-map detected activities to MITRE techniques |
| 📋 **Incident Summarization** | Generate executive summaries from multiple events |
| 📁 **Knowledge Upload** | Upload PDF/TXT/CSV docs to expand the knowledge base |
| 🔍 **IOC Extraction** | Automatically extract IPs, hashes, domains, URLs |
| ⚡ **Threat Classification** | Classify severity: Low, Medium, High, Critical |

---

## 🏗️ Architecture

```
         ┌────────────────┐
         │  User / SOC    │
         │   Analyst      │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │  FastAPI        │
         │  Backend        │
         │  (Port 8000)    │
         └───┬────────┬───┘
             │        │
             ▼        ▼
     ┌───────────┐ ┌──────────────┐
     │  Ollama   │ │  ChromaDB    │
     │  Qwen3 8B │ │  Vector DB   │
     │  (LLM)    │ │  (RAG)       │
     └───────────┘ └──────┬───────┘
                          │
                   ┌──────┴───────┐
                   │  Knowledge   │
                   │  Base        │
                   │  ─ MITRE     │
                   │  ─ Sigma     │
                   │  ─ OWASP     │
                   │  ─ NIST      │
                   └──────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.13) |
| LLM | Qwen3 8B via Ollama |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Store | ChromaDB |
| Containerization | Docker & Docker Compose |
| CI/CD | GitHub Actions |
| Orchestration | Kubernetes (Minikube) |
| Testing | Pytest |
| Code Quality | Flake8 |

---

## 📂 Project Structure

```
t14-ai/
│
├── backend/                        # 🔧 FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── api/
│   │   │   ├── chat.py             # Security Q&A endpoint
│   │   │   ├── analyze.py          # Log analysis & incident summary
│   │   │   └── upload.py           # Document upload endpoint
│   │   ├── rag/
│   │   │   ├── vectorstore.py      # ChromaDB vector store
│   │   │   ├── ingest.py           # Document ingestion pipeline
│   │   │   └── retriever.py        # RAG document retriever
│   │   ├── llm/
│   │   │   └── ollama_client.py    # Ollama LLM HTTP client
│   │   ├── services/
│   │   │   ├── log_analysis.py     # Log analysis service
│   │   │   ├── mitre_mapper.py     # MITRE ATT&CK mapper
│   │   │   └── summary_generator.py # Incident summary generator
│   │   └── models/
│   │       └── schemas.py          # Pydantic data models
│   ├── data/
│   │   ├── mitre/                  # MITRE ATT&CK knowledge base
│   │   ├── sigma/                  # Sigma detection rules
│   │   └── docs/                   # Security documentation
│   ├── tests/
│   │   ├── test_health.py          # Health endpoint tests
│   │   ├── test_chat.py            # Chat endpoint tests
│   │   └── test_log_analysis.py    # Log analysis tests
│   ├── Dockerfile                  # Backend container image
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # 🎨 Web UI
│   ├── index.html                  # Main HTML page
│   ├── style.css                   # Premium dark theme styles
│   └── app.js                      # Frontend application logic
│
├── k8s/                            # ☸️ Kubernetes (Bonus)
│   ├── deployment.yaml             # K8s deployment manifest
│   └── service.yaml                # K8s service manifest
│
├── .github/workflows/
│   └── ci.yml                      # GitHub Actions CI/CD pipeline
│
├── docker-compose.yml              # Multi-container orchestration
├── start.sh                        # One-command startup script
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

**Option A: Start everything together (Recommended)**
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/t14-ai.git
cd t14-ai

# 2. Start everything with one command
./start.sh
```

**Option B: Start individually (to showcase decoupled architecture)**
You can run the components in separate terminal windows to view their individual logs and demonstrate the microservices structure:

**Terminal 1 (LLM):**
```bash
./start-ollama.sh
```

**Terminal 2 (Backend):**
```bash
./start-backend.sh
```

**Terminal 3 (Frontend):**
```bash
./start-frontend.sh
```

### Access Points

| Service | URL |
|---------|-----|
| Web UI (Together) | http://localhost:8000 |
| Web UI (Individual) | http://localhost:8080 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Ollama | http://localhost:11434 |
| ChromaDB | http://localhost:8001 |

---

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "running",
  "model": "qwen3:8b",
  "rag_documents": 150
}
```

### Security Chat (RAG-Enhanced)

```http
POST /chat
```

**Request:**
```json
{
  "question": "What is Pass-the-Hash and how do I detect it?"
}
```

**Response:**
```json
{
  "answer": "Pass-the-Hash (PtH) is an attack technique where an adversary captures NTLM password hashes from memory and uses them to authenticate to other systems without knowing the plaintext password...\n\n**MITRE ATT&CK:** T1550.002\n\n**Detection Methods:**\n- Monitor Event ID 4624 with LogonType 3 and NTLM authentication\n- Look for anomalous NTLM authentication patterns\n...",
  "sources": ["mitre_attack_techniques.txt", "security_fundamentals.txt"]
}
```

### Log Analysis

```http
POST /analyze-log
```

**Request:**
```json
{
  "log": "Jun 15 10:23:01 server sshd[12345]: Failed password for root from 192.168.1.10 port 22 ssh2"
}
```

**Response:**
```json
{
  "severity": "Medium",
  "attack_type": "Brute Force",
  "mitre_technique": "T1110",
  "mitre_name": "Brute Force",
  "iocs": [
    {"type": "ip_address", "value": "192.168.1.10"}
  ],
  "recommendations": [
    "Enable MFA for the root account",
    "Review all login attempts from 192.168.1.10",
    "Consider disabling root SSH access"
  ],
  "summary": "Failed SSH login attempt for root account detected from 192.168.1.10, indicating possible brute force attack."
}
```

### Incident Summary

```http
POST /incident-summary
```

**Request:**
```json
{
  "events": [
    "Failed password for root from 192.168.1.10 port 22 ssh2",
    "Accepted password for admin from 10.0.0.5 port 22 ssh2",
    "PowerShell -encodedcommand detected in process creation logs"
  ]
}
```

### Upload Knowledge Base Document

```http
POST /upload-document
```

Upload PDF, TXT, CSV, or MD files via multipart form.

---

## 🔄 RAG Workflow

```
Step 1: Load cybersecurity documents (MITRE, Sigma, OWASP, NIST)
           ↓
Step 2: Chunk documents (500 chars, 100 char overlap)
           ↓
Step 3: Generate embeddings (Sentence Transformers)
           ↓
Step 4: Store vectors in ChromaDB
           ↓
Step 5: User asks question → Retrieve relevant chunks
           ↓
Step 6: Send context + question to Qwen3 8B
           ↓
Step 7: Return AI-generated response with source citations
```

---

## 🐳 Docker Deployment

### Architecture

```
         Docker Network (t14ai-network)
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐  ┌───────────┐  ┌──────────┐
│ FastAPI  │  │  Ollama   │  │ ChromaDB │
│ :8000   │  │  :11434   │  │  :8001   │
└─────────┘  └───────────┘  └──────────┘
```

### Commands

```bash
# Start all services
docker compose up --build -d

# View logs
docker compose logs -f app

# Stop all services
docker compose down

# Restart with fresh data
docker compose down -v
docker compose up --build -d
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

```
Git Push → Checkout → Flake8 → Pytest → Docker Build → Docker Push
```

Pipeline runs automatically on push to `main` or `develop` branches and on pull requests.

---

## ☸️ Kubernetes Deployment (Bonus)

```bash
# Deploy to Minikube
minikube start
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify
kubectl get pods -l app=t14ai-app
kubectl get svc t14ai-service

# Access
minikube service t14ai-service --url
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app

# Code quality check
flake8 app/ --max-line-length=120
```

---

## 📊 Screenshots

### Swagger UI
Access the interactive API documentation at: `http://localhost:8000/docs`

---

## 🔮 Future Improvements

- [ ] Splunk log ingestion integration
- [ ] ELK Stack integration
- [ ] Real-time IOC extraction pipeline
- [ ] Threat intelligence feed integration
- [ ] Production Kubernetes deployment
- [ ] Web-based dashboard enhancements
- [ ] Multi-model LLM support
- [ ] Automated Sigma rule generation

---

## 📋 Assignment Requirements Mapping

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| FastAPI Backend | FastAPI with 5 API endpoints | ✅ |
| LLM Integration (Ollama/OpenAI) | Qwen3 8B via Ollama | ✅ |
| RAG Implementation | ChromaDB + Sentence Transformers | ✅ |
| Dockerized Deployment | Dockerfile + Docker Compose (3 containers) | ✅ |
| GitHub Repository | Source control with .gitignore | ✅ |
| Documentation | Comprehensive README | ✅ |
| Swagger API Docs | Auto-generated at /docs | ✅ |
| MITRE Mapping | Automated technique mapping | ✅ |
| Log Analysis | Structured threat analysis | ✅ |
| Threat Detection | Severity classification + IOC extraction | ✅ |
| CI/CD | GitHub Actions | ✅ |
| Testing | Pytest with mocked dependencies | ✅ |
| Code Quality | Flake8 linting | ✅ |
| Kubernetes | Deployment + Service manifests | ✅ |

---

## 📜 License

This project is developed as part of an academic assignment and cybersecurity portfolio.

---

## 👤 Author

**T14 AI Team**

---

*Built with ❤️ for cybersecurity*
