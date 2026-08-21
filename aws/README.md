# CBTS Apex AI Platform

Enterprise Document Intelligence & Workflow Automation Platform built on AWS.

## Overview

Apex AI Platform enables enterprise clients to describe their work in plain English and deploy production-ready AI agents on AWS in weeks, not months.

### Platform Statistics

| Component | Count | Description |
|-----------|-------|-------------|
| Blueprints | 82 | Document extraction schemas |
| Playbooks | 71 | Workflow automations |
| Actions | 100 | Lambda business logic handlers |
| Industries | 20 | Complete vertical coverage |

> Counts reflect the verified seeded state (see the seeding step below). The
> same content ships in the `azure/` build.

---

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
cd apex-ai/aws
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
│   ├── src/
│   │   ├── components/    # UI components (BlueprintDesigner, WorkRoom, etc.)
│   │   ├── pages/         # Next.js pages
│   │   ├── lib/           # API client, Zustand store
│   │   └── styles/        # Tailwind CSS
│   └── package.json
│
├── backend/               # FastAPI application
│   ├── api/               # REST endpoints (22 routers)
│   ├── models/            # Pydantic models
│   ├── services/          # DynamoDB, S3, SQS, SageMaker, Bedrock, Action Registry
│   ├── core/              # Configuration
│   └── main.py
│
├── agentcore-agents/      # 32 Strands/AgentCore agents + deploy scripts
│
├── blueprints/            # Document extraction schemas (JSON, per industry)
│   ├── financial_services/
│   ├── healthcare_payers/
│   ├── nuclear_operations/
│   └── ... (22 industry folders)
│
├── playbooks/             # Workflow definitions (YAML, per industry)
│   ├── financial_services/
│   ├── healthcare_payers/
│   └── ... (20 industry folders + config/ + templates/)
│
├── actions/               # Action handlers (per industry)
│   ├── sdk/               # Apex Action SDK
│   ├── core/              # Core actions (BDA, DynamoDB, S3)
│   └── ... (20+ industry folders)
│
├── connectors/            # External system connectors
├── infrastructure/        # CloudFormation/SAM templates
├── sample-files/          # Sample input documents
├── synthetic-data/        # Test documents
├── scripts/               # Utility scripts
├── test-scripts/          # Ad-hoc test scripts
└── tests/                 # Test suite (unit, integration, api)
```

---

## 🏭 Industries Supported

Industry content lives in per-industry folders under `playbooks/`,
`blueprints/`, and `actions/`:

| | | | |
|---|---|---|---|
| aerospace_defense | agentic_enterprise | airlines | contact_center |
| cpg | credit_union | financial_services | healthcare_clinical |
| healthcare_payers | healthcare_providers | hr | insurance_underwriting |
| manufacturing | manufacturing_multi_division | nuclear_operations | oil_gas_midstream |
| retail | sales_ai | supply_chain | telecommunications |

---

## 🔌 API Endpoints

All endpoints are under `/api/v1`. Main resources:

### Playbooks
- `GET /api/v1/playbooks` - List all playbooks
- `POST /api/v1/playbooks` - Create playbook
- `POST /api/v1/playbooks/seed?industry={ind}` - Seed playbooks for an industry

### Blueprints
- `GET /api/v1/blueprints` - List all blueprints
- `POST /api/v1/blueprints` - Create blueprint
- `GET /api/v1/blueprints/{id}` - Get blueprint details
- `POST /api/v1/blueprints/seed?industry={ind}` - Seed blueprints for an industry

### Actions
- `GET /api/v1/actions` - List all actions
- `GET /api/v1/actions/gallery` - Action gallery by category
- `GET /api/v1/actions/packs` - Industry action packs
- `GET /api/v1/actions/registry/discover` - Discover all handlers
- `POST /api/v1/actions/registry/register-all` - Register all actions

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents/{id}/start` - Start agent
- `POST /api/v1/agents/{id}/stop` - Stop agent

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/{id}/extract` - Extract with blueprint

### Other routers
`work-items` · `chat` · `voice` · `pipelines` · `metrics` · `simulator` ·
`signals` · `llm` · `review-queue` · `aws` (admin) · `telecommunications` ·
`eprod` · `cwfcu` · `boler` · `inventory` · `jobs` · `import`

See Swagger at `/docs` for the full, always-accurate list.

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
| Queue | SQS |
| Predictive ML | SageMaker |
| Infrastructure | CloudFormation/SAM |

---

## License

Proprietary - CBTS Applied AI & Data Practice

## Contact

CBTS Applied AI & Data Practice - Accelerator Team
