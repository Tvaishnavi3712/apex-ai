# CBTS Apex AI Platform

Enterprise Document Intelligence & Workflow Automation Platform built on AWS.

## Overview

Apex AI Platform enables enterprise clients to describe their work in plain English and deploy production-ready AI agents on AWS in weeks, not months.

### Platform Statistics

| Component | Count | Description |
|-----------|-------|-------------|
| Blueprints | 34 | Document extraction schemas |
| Runbooks | 25 | Workflow automations |
| Actions | 56+ | Lambda business logic handlers |
| Industries | 12 | Complete vertical coverage |

---

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
cd /Users/babbu/Documents/CBTS/Accelerator/apex-ai-platform/aws
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
│   ├── api/               # REST endpoints (7 routers)
│   ├── models/            # Pydantic models
│   ├── services/          # DynamoDB, S3, Action Registry
│   ├── core/              # Configuration
│   └── main.py
│
├── blueprints/            # Document extraction schemas (34 JSON files)
│   ├── financial_services/
│   ├── healthcare_payers/
│   ├── healthcare_providers/
│   └── ... (12 industries)
│
├── runbooks/              # Workflow definitions (25 YAML files)
│   ├── financial_services/
│   ├── healthcare_payers/
│   └── ... (11 industries)
│
├── actions/               # Lambda handlers (56+ handlers)
│   ├── sdk/               # Apex Action SDK
│   ├── core/              # Core actions (BDA, DynamoDB, S3)
│   ├── healthcare_payers/ # 5 actions
│   ├── airlines/          # 5 actions
│   └── ... (11 industries)
│
├── tests/                 # Test suite (30 files)
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── api/               # API tests
│
├── synthetic-data/        # Test documents (50+ files)
├── infrastructure/        # CloudFormation templates
└── docs/                  # Documentation
```

---

## 🏭 Industries Supported

| Industry | Blueprints | Runbooks | Actions |
|----------|------------|----------|---------|
| Financial Services | 5 | 4 | 7 |
| Healthcare Payers | 3 | 2 | 5 |
| Healthcare Providers | 3 | 2 | 5 |
| Healthcare Clinical | 3 | 2 | 5 |
| Manufacturing | 4 | 3 | 3 |
| HR / Recruitment | 4 | 3 | 3 |
| Insurance Underwriting | 2 | 1 | 5 |
| Retail | 2 | 1 | 5 |
| CPG | 2 | 1 | 5 |
| Contact Center | 2 | 1 | 5 |
| Airlines | 2 | 2 | 5 |
| Supply Chain | 2 | 2 | 7 |

---

## 🔌 API Endpoints

### Blueprints
- `GET /api/v1/blueprints` - List all blueprints
- `POST /api/v1/blueprints` - Create blueprint
- `GET /api/v1/blueprints/{id}` - Get blueprint details

### Runbooks
- `GET /api/v1/runbooks` - List all runbooks
- `POST /api/v1/runbooks` - Create runbook
- `POST /api/v1/runbooks/{id}/deploy` - Deploy runbook

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
| Agent Runtime | Bedrock AgentCore |
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
