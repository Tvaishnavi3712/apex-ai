# Skill: Create Blueprint

When asked to create a new blueprint for document extraction:

## Blueprint Structure
```json
{
  "blueprintName": "apex-{document-type}-v1",
  "blueprintStage": "DEVELOPMENT",
  "schema": {
    "bdaSchema": {
      "description": "Schema for extracting data from {document type}",
      "documentClass": "{document_class}",
      "documentType": "{document_type}",
      "attributes": []
    }
  }
}
```

## Attribute Format
```json
{
  "name": "field_name",
  "type": "string|number|date|array|boolean",
  "inferenceType": "explicit",
  "instruction": "Extract the {field description} from the document"
}
```

## Array Items Format
```json
{
  "name": "line_items",
  "type": "array",
  "inferenceType": "explicit",
  "instruction": "Extract all line items from the document",
  "items": {
    "type": "object",
    "attributes": [
      {"name": "description", "type": "string"},
      {"name": "quantity", "type": "number"},
      {"name": "unit_price", "type": "number"},
      {"name": "amount", "type": "number"}
    ]
  }
}
```

## Location
Save blueprints to: `blueprints/{industry}/{document_type}.json`

## Industries
- financial_services
- healthcare_payers
- healthcare_providers
- healthcare_clinical
- manufacturing
- hr
- insurance_underwriting
- retail
- cpg
- contact_center
- airlines
- supply_chain
