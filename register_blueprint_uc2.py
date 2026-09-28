import json, urllib.request

src = json.load(open('aws/blueprints/insurance_underwriting/cp_submission_packet.json', encoding='utf-8'))
bda = src['bdaSchema']
defs = bda.get('definitions', {})

fields = []
for fname, fdef in bda['properties'].items():
    f = {'name': fname, 'type': fdef.get('type', 'string'),
         'description': fdef.get('instruction', ''), 'required': False}
    if fdef.get('type') == 'array':
        ref = fdef.get('items', {}).get('$ref', '').split('/')[-1]
        if ref in defs:
            f['items'] = {'type': 'object', 'properties': {
                k: {'type': v.get('type', 'string'),
                    'description': v.get('instruction', '')}
                for k, v in defs[ref]['properties'].items()}}
    fields.append(f)

payload = {
    'name': 'cp_submission_packet',
    'description': bda.get('description', ''),
    'industry': 'insurance_underwriting',
    'document_type': 'cp_submission_packet',
    'version': '1.0.0',
    'schema_fields': fields,
    'extraction_instructions': bda.get('extractionInstructions', ''),
}

req = urllib.request.Request(
    'http://localhost:8000/api/v1/blueprints/',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}, method='POST')
resp = urllib.request.urlopen(req)
print(resp.status)
print(resp.read().decode()[:400])
