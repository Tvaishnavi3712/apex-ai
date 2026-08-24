# CBTS Apex AI Platform

## Project Overview
Enterprise Document Intelligence & Workflow Automation Platform built on AWS. Enables business users to describe work in plain English and deploy production-ready AI agents.

## Tech Stack

### Frontend
- **Framework:** Next.js 16 with React 18
- **Language:** TypeScript 5.x
- **Styling:** Tailwind CSS 3.x
- **State Management:** Zustand 4.x
- **Charts:** Recharts 2.x
- **Icons:** Heroicons 2.x

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Validation:** Pydantic 2.x
- **AWS SDK:** boto3
- **Async:** httpx, aiofiles

### AWS Services
- **AI:** Bedrock Data Automation (BDA), Bedrock AgentCore
- **Database:** DynamoDB
- **Storage:** S3
- **Auth:** Cognito
- **Compute:** Lambda
- **Infrastructure:** CloudFormation/SAM

## Folder Structure

```
aws/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── BlueprintDesigner/
│   │   │   ├── CommandCenter/  # Monitoring & metrics (formerly ControlRoom)
│   │   │   ├── PlaybookBuilder/
│   │   │   ├── AgentHub/       # Agent chat & queue (formerly WorkRoom)
│   │   │   ├── Layout/
│   │   │   └── common/
│   │   ├── pages/            # Next.js pages (13 pages)
│   │   ├── lib/              # API client, Zustand store
│   │   └── styles/           # Tailwind CSS
│   └── package.json
│
├── backend/                  # FastAPI application
│   ├── api/                  # REST endpoints (8 router files)
│   │   ├── playbooks.py
│   │   ├── agents.py
│   │   ├── blueprints.py
│   │   ├── documents.py
│   │   ├── work_items.py
│   │   ├── chat.py
│   │   ├── voice.py
│   │   └── actions.py
│   ├── models/               # Pydantic models (5 models)
│   ├── services/             # DynamoDB, S3, ActionRegistry
│   ├── core/                 # Configuration
│   └── main.py
│
├── agentcore-agents/         # Strands/AgentCore agents + deploy scripts
│
├── blueprints/               # Document extraction schemas (42 JSON)
│   ├── financial_services/
│   ├── healthcare_payers/
│   ├── healthcare_providers/
│   ├── healthcare_clinical/
│   ├── manufacturing/
│   ├── hr/
│   └── ... (13 industries)
│
├── playbooks/                # Workflow definitions (38 YAML)
│   ├── financial_services/
│   ├── healthcare_payers/
│   └── ... (13 industries + config/ + templates/)
│
├── actions/                  # Action handlers (202 Python files)
│   ├── sdk/                  # Apex Action SDK
│   ├── core/                 # BDA, DynamoDB, S3, Notification
│   ├── integrations/         # External system integrations
│   ├── financial_services/
│   ├── healthcare_payers/
│   └── ... (13 industries, incl. sales_ai/)
│
├── tests/                    # Test suite (23 files)
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── api/                  # API tests
│
├── synthetic-data/           # Test documents
├── infrastructure/           # CloudFormation templates
└── docs/                     # Documentation
    ├── apex-deployment-playbook.md  # Enterprise deployment guide
    └── templates/                    # Assessment templates
        ├── use-case-scoring-matrix.md
        ├── viability-assessment-checklist.md
        └── six-key-metrics-template.md
```

## Key Commands

See `README.md` → Prerequisites for AWS CLI v2 setup (install from the official AWS source, never from a binary committed to this repo).

### Development
```bash
# Start everything
./start.sh

# Backend only
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Frontend only
cd frontend && npm run dev

# Run tests
cd backend && pytest tests/ -v --cov=.
cd frontend && npm test
```

### API Endpoints
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Code Style

### Python (Backend)
- Use type hints for all functions
- Pydantic models for request/response validation
- Async functions for I/O operations
- Follow PEP 8 naming conventions
- Use `@apex_action` decorator for Lambda handlers

### TypeScript (Frontend)
- Strict mode enabled
- Use interfaces for component props
- Functional components with hooks
- Path aliases: `@/components/*`, `@/lib/*`

### Blueprints (JSON)
- Follow BDA schema format with `bdaSchema` wrapper
- Include explicit extraction instructions
- Define field types: string, number, date, array, boolean

### Playbooks (YAML)
- Follow Intent → Output → Context → Recipe pattern
- Natural language instructions
- Map actions to Lambda handlers

## Platform Statistics

| Component | Count |
|-----------|-------|
| Frontend Pages | 13 |
| Frontend Components | 17 |
| Backend API Routers | 8 |
| Blueprints | 42 |
| Playbooks | 38 |
| Actions | 202 |
| Tests | 23 |
| Industries | 13 |
| **Total Artifacts** | **343** |

> Blueprint/playbook/action/industry counts measured from the repo (Aug 2026);
> frontend/test counts need verification in the baseline audit (APEX-17).

## Industries Supported
1. Financial Services
2. Healthcare Payers
3. Healthcare Providers
4. Healthcare Clinical
5. Manufacturing
6. HR / Recruitment
7. Insurance Underwriting
8. Retail
9. CPG
10. Contact Center
11. Airlines
12. Supply Chain
13. Sales AI

## Important Notes

- **Mock Data:** Frontend currently uses mock data, API integration pending
- **AWS Integration:** BDA and AgentCore integration not yet complete
- **Authentication:** Cognito integration designed but not implemented
- **Production Readiness:** 60-90 days from pilot pending integrations

## UI Naming Convention

| Section | Name | Purpose | Route |
|---------|------|---------|-------|
| Workflow Builder | **Canvas** | Design playbooks & blueprints | `/canvas` |
| Monitoring | **Command Center** | Agent metrics & monitoring | `/command-center` |
| Interaction | **Agent Hub** | Chat with agents, work queue | `/agent-hub` |
| Tools | **Actions** | Lambda action handlers | `/actions` |

## Agent Naming Convention
- InvoiceBot, VendorBot (Financial Services)
- ClaimsBot, AuthBot (Healthcare Payers)
- IntakeBot (Healthcare Providers)
- POBot, QCBot (Manufacturing)
- TalentBot (HR)
- DisruptBot (Airlines)
- ReturnsBot (Retail)
- UnderwriteBot (Insurance)
- QABot (Contact Center)
- InventoryBot (Supply Chain)

## APEX Deployment Framework

Four-phase methodology for enterprise deployment:

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Discovery & Assessment | 1-2 weeks | Process mapping, document inventory, stakeholder alignment |
| 2. Use Case Selection | 1-2 weeks | Scoring matrix, viability assessment, ROI model, pilot planning |
| 3. Implementation | 4-6 weeks | Blueprint config, playbook development, integration, testing |
| 4. Launch & Scale | Ongoing | Phased rollout, change management, monitoring, optimization |

### Six Key Metrics
1. **Documents Processed** - Volume throughput
2. **Extraction Accuracy** - Quality (target: ≥95%)
3. **Processing Time** - Speed (target: <5s extraction)
4. **Cost Per Document** - Efficiency (target: <$2.00)
5. **Automation Rate** - Adoption (target: ≥80%)
6. **User Satisfaction** - Experience (target: ≥4.0/5.0)

See `docs/apex-deployment-playbook.md` for full methodology.
