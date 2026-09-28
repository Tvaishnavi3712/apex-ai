import json, urllib.request

src = json.load(open('ap_exception_packet.json', encoding='utf-8'))
bda = src['bdaSchema']
defs = bda.get('definitions', {})
DATE_FIELDS = {'invoice_date', 'due_date'}

fields = []
for fname, fdef in bda['properties'].items():
    ftype = 'date' if fname in DATE_FIELDS else fdef.get('type', 'string')
    f = {'name': fname, 'type': ftype,
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
    'name': 'ap_exception_packet',
    'description': bda.get('description', ''),
    'industry': 'financial_services',
    'document_type': 'ap_exception_packet',
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