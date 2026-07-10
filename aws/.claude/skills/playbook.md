# Skill: Create Playbook

When asked to create a new playbook for workflow automation:

## Playbook Structure (YAML)
```yaml
playbook:
  name: "{workflow-name}"
  version: "1.0"
  description: "{Brief description}"
  industry: "{industry}"
  document_type: "{document_type}"

intent: |
  {Natural language description of what this playbook accomplishes}

output:
  success_criteria:
    - "{Measurable outcome 1}"
    - "{Measurable outcome 2}"
  deliverables:
    - "{Output 1}"
    - "{Output 2}"

context:
  triggers:
    - type: "{s3_event|api_call|schedule|workflow}"
      config:
        {trigger-specific configuration}

  variables:
    {variable_name}: "{description}"

recipe: |
  ## Workflow Steps

  ### Step 1: {Step Name}
  {Natural language instructions}

  ### Step 2: {Step Name}
  {Natural language instructions}

actions:
  - name: "{action_name}"
    action_id: "{action_id}"
    description: "{When to use this action}"
    required: true|false

worker:
  type: "apex-agent"
  config:
    model: "anthropic.claude-opus-4-5-20251101-v1:0"
    max_concurrent: 10
    timeout_seconds: 300

error_handling:
  on_extraction_failure: "queue_for_review"
  on_validation_failure: "notify_and_retry"
  max_retries: 3
  escalation_path: "human_review_queue"
```

## Location
Save playbooks to: `playbooks/{industry}/{workflow_name}.yaml`

## Action IDs Available
### Core
- bda_extract
- dynamodb_lookup
- s3_operations
- notification

### Financial Services
- vendor_lookup
- po_match
- approval_route
- compliance_check

### Healthcare
- claims_adjudication
- eligibility_verify
- medical_necessity
- prior_auth
- ehr_lookup
- patient_lookup
