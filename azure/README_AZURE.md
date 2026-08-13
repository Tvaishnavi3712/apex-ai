# APEX on Azure

The Azure-native build of Apex — same application, same demo modes, same UX,
built entirely on Azure services. There are **no AWS SDKs, service names, or
identifiers anywhere in this folder.**

Runs on **ports 3002 / 8002** so it can run side-by-side with the AWS build.

---

## 1. Quick start

```bash
# Backend
cd backend
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
set -a && source .env.azure && set +a
./venv/bin/uvicorn main:app --reload --port 8002
```

```bash
# Frontend (new terminal)
cd frontend
npm install
npx next dev --port 3002
```

Open **http://localhost:3002** · API docs at **http://localhost:8002/docs**

### Seed the data (first run only — it persists after that)

```bash
for ind in $(ls playbooks/ | grep -vE "config|templates"); do
  curl -s -X POST "http://localhost:8002/api/v1/playbooks/seed?industry=$ind&force=true" -o /dev/null
  curl -s -X POST "http://localhost:8002/api/v1/blueprints/seed?industry=$ind&force=true" -o /dev/null
done
curl -s -X POST "http://localhost:8002/api/v1/actions/registry/reload"
curl -s -X POST "http://localhost:8002/api/v1/actions/registry/register-all"
```

Verified state: **71 playbooks · 82 blueprints · 100 actions · 71 pipelines**.

---

## 2. Architecture

| Capability | Azure service | Implementation |
|---|---|---|
| Table store | **Cosmos DB (NoSQL)** | `services/cosmos.py` |
| Object store | **Blob Storage** | `services/blob.py` |
| Model router | **Azure OpenAI** (GPT-5 family) | `services/azure_openai.py` |
| Agent runtime | **Azure AI Foundry Agent Service** | `services/foundry_agent.py` |
| Document extraction | **Azure AI Document Intelligence** | `services/doc_intelligence.py` |
| Predictive ML | **Azure ML** online endpoints | `services/azure_ml.py` |
| Queue | **Azure Service Bus** | `services/queue.py` |
| Secrets | **Key Vault** | provisioned |
| Identity | **Microsoft Entra ID** | `DefaultAzureCredential` |
| Local fallback | disk-persisted store | `services/local_store.py` |

Cloud-neutral logic lives in `services/agent_simulators.py` (demo reasoning) and
`services/prediction_base.py` (prediction logic); the Azure adapters above supply
the transport.

### Models

| Tier | Deployment |
|---|---|
| `fast` | `gpt-5-mini` |
| `balanced` *(default)* | `gpt-5.4` |
| `quality` | `gpt-5.4` |
| `embeddings` | `text-embedding-3-small` |

> `gpt-5-pro` is a reasoning model served **only** by the Responses API and
> returns HTTP 400 on `chat.completions`, so the quality tier uses `gpt-5.4`.
> Override with `AZURE_OPENAI_DEPLOYMENT*` in `.env.azure`.

---

## 3. Agents

32 agents live in **`foundry-agents/`**. `foundry_runtime.py` provides the agent
primitives (`FoundryAgentApp`, `Agent`, `tool`, `AzureOpenAIModel`); tools are
dispatched in-process via Azure OpenAI function calling.

```bash
python foundry-agents/deploy_foundry_agents.py --list   # 32 agents
python foundry-agents/deploy_foundry_agents.py --all    # provision to Foundry
export AZURE_FOUNDRY_AGENTS="$(cat foundry-agents/foundry_agents.json)"
```

Agents without a provisioned Foundry id run on the in-process runtime — the path
the demos use, with no cold start.

---

## 4. Actions

Action handlers use two compatibility shims so their bodies stay declarative:

| Shim | Purpose |
|---|---|
| `actions/sdk/azure_llm.py` | `invoke_model()` over Azure OpenAI (handles multimodal blocks) |
| `actions/sdk/azure_data.py` | `Table().get_item/put_item/query/scan` over Cosmos DB |

Both fall back to the local store / mock when Azure is unreachable, so a handler
never hard-fails a pipeline.

---

## 5. Infrastructure

`infrastructure/azure/main.bicep` provisions into resource group
**`manish-dev-apex-ai-coe`** (eastus, subscription `sbx-data-ai-coe-sub`):

| Resource | Name |
|---|---|
| Cosmos DB (serverless, 23 containers, db `apex`) | `apexcoe-cosmos` |
| Storage (4 containers) | `apexcoestg` |
| Key Vault | `apexcoe-kv` |
| VNet (`snet-private-endpoints`, `snet-apps`) | `apexcoe-vnet` |
| Private endpoints + private DNS | 3 |

```bash
az deployment group create -g manish-dev-apex-ai-coe \
  --template-file infrastructure/azure/main.bicep --parameters prefix=apexcoe
```

### ⚠️ Everything is private, by policy

The subscription inherits the Azure Landing Zone policy set
**`Deny-PublicPaaSEndpoints`** (management group `mg-alz-sandbox`), which
hard-denies any PaaS resource with public network access:

* Storage → `publicNetworkAccess: Disabled` + `allowBlobPublicAccess: false`
* Cosmos → `publicNetworkAccess: Disabled`
* Cognitive Services → `publicNetworkAccess: Disabled` + `networkAcls.defaultAction: Deny`

Pre-existing resources that look public are **grandfathered** — Deny policies
block new/updated resources, they don't retro-delete.

**Consequence:** Cosmos and Blob are reachable only from inside the VNet, not
from a laptop. Local development uses the persisted local store; deployed compute
(Container Apps in `snet-apps`) talks to the real services.

---

## 6. Local development

Mocking is **per service**, so you get **real AI over local data** — Azure OpenAI
is publicly reachable while Cosmos/Blob are not.

| Flag | Default | Effect |
|---|---|---|
| `USE_LOCAL_MOCK` | `true` | Global default for all adapters |
| `AZURE_OPENAI_MOCK` | `false` | **Real** Azure OpenAI even locally |
| `AZURE_DOCINTEL_MOCK` | inherits | Document Intelligence mock |
| `AZURE_FOUNDRY_MOCK` | inherits | Agent runtime mock |

The table store persists to disk, so seeded data survives a restart:

```bash
APEX_MOCK_PERSIST=true                      # false = pure in-memory
APEX_MOCK_FILE=/tmp/apex-mock-store.json
```

Reset local data: `rm /tmp/apex-mock-store.json` and re-seed.

---

## 7. Auth

Entra ID via `DefaultAzureCredential` — **no keys or connection strings anywhere**.
Cosmos uses `disableLocalAuth: true`, Storage uses `allowSharedKeyAccess: false`,
so key auth is not possible.

```bash
az login
az account set --subscription sbx-data-ai-coe-sub
```

> **Data-plane RBAC:** calling Azure OpenAI requires the **Cognitive Services
> OpenAI User** role on the resource. `Owner`/`Contributor` are control-plane only
> and are *not* sufficient. Propagation takes ~5 minutes.
> ```bash
> az role assignment create --assignee-object-id <object-id> \
>   --assignee-principal-type User --role "Cognitive Services OpenAI User" \
>   --scope <cognitive-services-account-resource-id>
> ```

---

## 8. Ports

| | AWS build | Azure build |
|---|---|---|
| Frontend | 3000 | **3002** |
| Backend | 8001 | **8002** |

Both can run simultaneously; `CORS_ORIGINS` allows all four.

> **Restarting the backend:** always `lsof -ti:8002 | xargs kill -9`. A plain
> `kill` can leave a stale uvicorn holding the port, which then serves old code.

---

## 9. Data formats

Blueprints use a **`documentSchema`** wrapper (the seeder also accepts top-level
`schema.properties` and `schema_fields`):

```json
{
  "name": "invoice",
  "industry": "financial_services",
  "documentSchema": {
    "fields": {
      "invoice_number": { "type": "string", "required": true }
    }
  }
}
```

Logical table names (`apex-ai-platform-playbooks`) map to Cosmos containers
(`playbooks`) by stripping `APEX_TABLE_PREFIX`. Partition keys: `/industry` for
playbooks and blueprints, `/scenario_id` for simulator scenarios, `/id` elsewhere.

---

## 10. Still to build

1. **Container Apps** deployment + Event Grid blob trigger.
2. **Azure AI Search** index for knowledge/vector retrieval.
3. Provision **Document Intelligence** + **Azure ML** resources (adapters are
   ready and pick them up from `.env.azure`).
4. **Responses API** support so the quality tier can use `gpt-5-pro`.
