# CBTS Apex AI Platform

Enterprise Document Intelligence & Workflow Automation Platform built on AWS.

## Overview

Apex AI Platform enables enterprise clients to describe their work in plain English and deploy production-ready AI agents on AWS in weeks, not months.

### Platform Statistics

| Component | Count | Description |
|-----------|-------|-------------|
| Blueprints | 42 | Document extraction schemas (JSON) |
| Playbooks | 38 | Workflow automations (YAML) |
| Actions | 202 | Action handler files (Python) |
| Industries | 13 | Vertical coverage |

> Counts measured directly from the repo (Aug 2026): `Get-ChildItem -Recurse`
> over `blueprints/*.json`, `playbooks/*.yaml`, and `actions/*.py`.

---

## ✅ Prerequisites

- Python 3.11+
- Node.js 18+
- **AWS CLI v2** — install from the official source for your platform, never from a binary committed to this repo:
  - macOS: `curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg" && sudo installer -pkg AWSCLIV2.pkg -target /` (or `brew install awscli`)
  - Linux: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install`
  - Windows: [official MSI installer](https://awscli.amazonaws.com/AWSCLIV2.msi), or `winget install Amazon.AWSCLI`
  - Verify with `aws --version` (expect `aws-cli/2.x`)
  - Note: the `awscli` package on PyPI (`pip install awscli`) tracks CLI **v1** — it is not a drop-in replacement for v2
- Configured AWS credentials (`aws configure` or `aws configure sso`) with access to the target account's Bedrock, DynamoDB, and S3 resources

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
cd cbts-tool-apexai/aws
./start.sh
```

This will automatically:
- Set up Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Start both services

### Option 2: Manual Startup

#### Terminal 1 - Backend API

```bash
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

#### Terminal 2 - Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Service status |

---

## 📁 Project Structure

```
aws/
├── frontend/              # Next.js React application
│   └── src/               # components, pages, lib (API client, Zustand), styles
│
├── backend/               # FastAPI application
│   ├── api/               # REST endpoints (8 routers: actions, agents,
│   │                      #   blueprints, chat, documents, playbooks,
│   │                      #   voice, work_items)
│   ├── models/            # Pydantic models
│   ├── services/          # DynamoDB, S3, Bedrock, Action Registry
│   ├── core/              # Configuration
│   └── main.py
│
├── agentcore-agents/      # Strands/AgentCore agents + deploy scripts
│
├── blueprints/            # 42 document extraction schemas (JSON, 13 industries)
│
├── playbooks/             # 38 workflow definitions (YAML, 13 industries
│   │                      #   + config/ + templates/)
│
├── actions/               # 202 handler files
│   ├── sdk/               # Apex Action SDK
│   ├── core/              # Core actions (BDA, DynamoDB, S3)
│   ├── integrations/      # External system integrations
│   └── ... (13 industry folders, incl. sales_ai/)
│
├── docs/                  # Documentation
├── infrastructure/        # CloudFormation/SAM templates
├── synthetic-data/        # Test documents
├── tests/                 # Test suite (unit, integration, api)
├── CLAUDE.md              # Claude Code project instructions
└── start.sh               # One-command local startup
```

---

## 🏭 Industries Supported

Industry content lives in per-industry folders under `playbooks/`, `blueprints/`, and `actions/`:

| | | |
|---|---|---|
| airlines | contact_center | cpg |
| financial_services | healthcare_clinical | healthcare_payers |
| healthcare_providers | hr | insurance_underwriting |
| manufacturing | retail | sales_ai |
| supply_chain | | |

---

## 🔌 API Endpoints

All endpoints are under `/api/v1` (8 routers — see `backend/api/`).

### Playbooks
- `GET /api/v1/playbooks` - List all playbooks
- `POST /api/v1/playbooks` - Create playbook

### Blueprints
- `GET /api/v1/blueprints` - List all blueprints
- `POST /api/v1/blueprints` - Create blueprint
- `GET /api/v1/blueprints/{id}` - Get blueprint details

### Actions
- `GET /api/v1/actions` - List all actions (registry, gallery, packs)

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents/{id}/start` - Start agent
- `POST /api/v1/agents/{id}/stop` - Stop agent

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/{id}/extract` - Extract with blueprint

### Other routers
`chat` · `voice` · `work-items`

See Swagger at `/docs` for the complete, always-accurate list.

---

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)
```env
DEBUG=true
ENVIRONMENT=development
AWS_REGION=us-east-1
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🔧 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Module not found
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && rm -rf node_modules && npm install
```

### CORS errors
Ensure backend is running on port 8000 before starting frontend.

---

## Architecture

- **Apex Studio**: Zero-code agent builder with AI copilot
- **Apex Agent Runtime**: Bedrock AgentCore for AI-native orchestration
- **Apex Document Engine**: Bedrock Data Automation for document processing
- **Apex Actions**: AgentCore Gateway for tool integration
- **Apex Work Room**: Employee interaction workspace
- **Apex Control Room**: Deployment and monitoring dashboard

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14 + React 18 + TypeScript |
| Backend | Python FastAPI |
| State Management | Zustand |
| Styling | Tailwind CSS |
| Agent Runtime | Bedrock AgentCore (Strands agents in `agentcore-agents/`) |
| Document Processing | Bedrock Data Automation |
| Actions/Tools | AgentCore Gateway + Lambda |
| Database | DynamoDB |
| Storage | S3 |
| Infrastructure | CloudFormation/SAM |

---

## License

Proprietary - CBTS Applied AI & Data Practice

## Contact

CBTS Applied AI & Data Practice - Accelerator Team
