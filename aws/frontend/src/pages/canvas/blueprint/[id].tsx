/**
 * Blueprint Detail — fully editable field mapper + BDA schema for a single
 * blueprint. The page is id-aware: CBB demo blueprints (bp-cbb-order, bp-cbb-qc,
 * bp-cbb-disrupt) load their own data; anything else falls back to the generic
 * Invoice Blueprint v2 shape so deep links still render.
 *
 * Tabs:
 *   Fields            — editable rows + per-field validation rules (inline expand)
 *   Virtual Fields    — computed fields (editable)
 *   Blueprint Rules   — blueprint-wide rules (editable)
 *   JSON Preview      — live preview of the BDA schema JSON driven by state
 */

import React, { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import { humanizeName } from '@/lib/humanize';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types ═════════════════════ */

type Tab = 'fields' | 'virtual' | 'rules' | 'preview';
type FieldType = 'string' | 'number' | 'date' | 'boolean' | 'array' | 'enum' | 'object';
type RuleKind  = 'required' | 'min' | 'max' | 'min_length' | 'max_length' | 'regex' | 'enum_values' | 'date_range' | 'custom';

interface ValidationRule {
  id: string;
  kind: RuleKind;
  value: string;           // stored as string; interpreted per rule kind
  error_message: string;
}

interface Field {
  name: string;
  desc: string;
  type: FieldType;
  confidence: number;
  required: boolean;
  validations: ValidationRule[];
}

interface VirtualField {
  name: string;
  formula: string;
  type: FieldType;
}

interface BlueprintRule {
  label: string;
  detail: string;
  active: boolean;
}

interface BlueprintData {
  id: string;
  name: string;
  version: string;
  description: string;
  industry_label: string;
  status_label: string;
  status_chip: string;        // chip-green / chip-amber / chip-gray
  arn: string;
  document_class: string;
  industry_key: string;       // e.g. "financial_services"
  fields: Field[];
  virtual_fields: VirtualField[];
  blueprint_rules: BlueprintRule[];
}

/* ═════════════════════ rule metadata ═════════════════════ */

const RULE_TYPES: { kind: RuleKind; label: string; hint: string; appliesTo: FieldType[] }[] = [
  { kind: 'required',    label: 'Required',           hint: 'Field must be present',                   appliesTo: ['string','number','date','boolean','array','enum','object'] },
  { kind: 'min',         label: 'Minimum value',      hint: 'Numeric lower bound (e.g. 0.01)',         appliesTo: ['number'] },
  { kind: 'max',         label: 'Maximum value',      hint: 'Numeric upper bound (e.g. 10000000)',     appliesTo: ['number'] },
  { kind: 'min_length',  label: 'Min length',         hint: 'Min chars / items',                        appliesTo: ['string','array'] },
  { kind: 'max_length',  label: 'Max length',         hint: 'Max chars / items',                        appliesTo: ['string','array'] },
  { kind: 'regex',       label: 'Regex pattern',      hint: 'e.g. ^CBB-ORD-\\d{4,8}$',                  appliesTo: ['string'] },
  { kind: 'enum_values', label: 'Allowed values',     hint: 'Comma-separated list',                     appliesTo: ['string','enum'] },
  { kind: 'date_range',  label: 'Date range',         hint: 'YYYY-MM-DD..YYYY-MM-DD (either side opt)', appliesTo: ['date'] },
  { kind: 'custom',      label: 'Custom expression',  hint: 'Free-form business rule',                  appliesTo: ['string','number','date','boolean','array','enum','object'] },
];

const RULE_LABEL: Record<RuleKind, string> = Object.fromEntries(
  RULE_TYPES.map(r => [r.kind, r.label]),
) as Record<RuleKind, string>;

const applicableRuleKinds = (ft: FieldType): RuleKind[] =>
  RULE_TYPES.filter(r => r.appliesTo.includes(ft)).map(r => r.kind);

const newRule = (kind: RuleKind, ft: FieldType): ValidationRule => {
  const defaults: Partial<Record<RuleKind, string>> = {
    required:    '',
    min:         '0',
    max:         ft === 'number' ? '1000000' : '',
    min_length:  '1',
    max_length:  '255',
    regex:       '',
    enum_values: '',
    date_range:  '',
    custom:      '',
  };
  return {
    id: `r-${Math.random().toString(36).slice(2, 9)}`,
    kind,
    value: defaults[kind] ?? '',
    error_message: defaultErrorMessage(kind),
  };
};

function defaultErrorMessage(kind: RuleKind): string {
  switch (kind) {
    case 'required':    return 'This field is required.';
    case 'min':         return 'Value must be greater than or equal to {value}.';
    case 'max':         return 'Value must be less than or equal to {value}.';
    case 'min_length':  return 'Must be at least {value} characters.';
    case 'max_length':  return 'Must be no more than {value} characters.';
    case 'regex':       return 'Value does not match the required format.';
    case 'enum_values': return 'Value must be one of: {value}.';
    case 'date_range':  return 'Date must fall within {value}.';
    case 'custom':      return 'Value violates business rule.';
  }
}

/* ═════════════════════ component ═════════════════════ */

export default function BlueprintDetailPage() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : '';

  // API-first — see CLAUDE.md "No hardcoding" rule. Fall back to the local
  // registry only on 404 / network failure so offline dev still works.
  const apiQuery = useQuery<any>({
    queryKey: ['blueprint', id],
    queryFn: async () => {
      if (!id) return null;
      const r = await fetch(`${API_BASE_URL}/blueprints/${encodeURIComponent(id)}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    enabled: !!id,
    retry: false,
    staleTime: 30_000,
  });

  const bp = useMemo<BlueprintData>(() => {
    if (apiQuery.data) return _apiToBlueprintData(apiQuery.data);
    if (apiQuery.isError) return lookupBlueprint(id);
    return EMPTY_BLUEPRINT;
  }, [apiQuery.data, apiQuery.isError, id]);

  const [tab, setTab] = useState<Tab>('fields');

  // Editable state — seeded per id
  const [name, setName]                     = useState(bp.name);
  const [version, setVersion]               = useState(bp.version);
  const [description, setDescription]       = useState(bp.description);
  const [fields, setFields]                 = useState<Field[]>(bp.fields);
  const [virtualFields, setVirtualFields]   = useState<VirtualField[]>(bp.virtual_fields);
  const [bpRules, setBpRules]               = useState<BlueprintRule[]>(bp.blueprint_rules);
  const [expandedField, setExpandedField]   = useState<string | null>(null);
  const [toast, setToast]                   = useState<string | null>(null);
  const [showDeployModal, setShowDeployModal] = useState(false);

  useEffect(() => {
    setName(bp.name);
    setVersion(bp.version);
    setDescription(bp.description);
    setFields(bp.fields);
    setVirtualFields(bp.virtual_fields);
    setBpRules(bp.blueprint_rules);
    setExpandedField(null);
  }, [bp]);

  const showToast = (msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 2200);
  };

  const avgConfidence = fields.length === 0
    ? 0
    : Math.round((fields.reduce((s, f) => s + f.confidence, 0) / fields.length) * 10) / 10;

  /* ── field CRUD ── */
  const updateField = (i: number, patch: Partial<Field>) =>
    setFields(list => list.map((f, idx) => idx === i ? { ...f, ...patch } : f));

  const removeField = (i: number) =>
    setFields(list => list.filter((_, idx) => idx !== i));

  const addField = () => {
    const f: Field = {
      name: `new_field_${fields.length + 1}`,
      desc: 'Describe this field',
      type: 'string',
      confidence: 90,
      required: false,
      validations: [],
    };
    setFields([...fields, f]);
    setExpandedField(f.name);
  };

  const updateFieldType = (i: number, nextType: FieldType) => {
    const allowed = new Set(applicableRuleKinds(nextType));
    setFields(list => list.map((f, idx) => {
      if (idx !== i) return f;
      return {
        ...f,
        type: nextType,
        // drop rules that don't apply to the new type
        validations: f.validations.filter(v => allowed.has(v.kind)),
      };
    }));
  };

  /* ── rule CRUD per field ── */
  const addRule = (fi: number, kind: RuleKind) =>
    setFields(list => list.map((f, idx) =>
      idx === fi ? { ...f, validations: [...f.validations, newRule(kind, f.type)] } : f,
    ));

  const updateRule = (fi: number, ri: number, patch: Partial<ValidationRule>) =>
    setFields(list => list.map((f, idx) => {
      if (idx !== fi) return f;
      return { ...f, validations: f.validations.map((r, j) => j === ri ? { ...r, ...patch } : r) };
    }));

  const removeRule = (fi: number, ri: number) =>
    setFields(list => list.map((f, idx) => {
      if (idx !== fi) return f;
      return { ...f, validations: f.validations.filter((_, j) => j !== ri) };
    }));

  /* ── virtual fields ── */
  const updateVirtual = (i: number, patch: Partial<VirtualField>) =>
    setVirtualFields(list => list.map((v, idx) => idx === i ? { ...v, ...patch } : v));
  const addVirtual    = () => setVirtualFields([...virtualFields, { name: 'new_computed_field', formula: '', type: 'string' }]);
  const removeVirtual = (i: number) => setVirtualFields(list => list.filter((_, idx) => idx !== i));

  /* ── blueprint-wide rules ── */
  const updateBpRule = (i: number, patch: Partial<BlueprintRule>) =>
    setBpRules(list => list.map((r, idx) => idx === i ? { ...r, ...patch } : r));
  const addBpRule    = () => setBpRules([...bpRules, { label: 'New Rule', detail: '', active: true }]);
  const removeBpRule = (i: number) => setBpRules(list => list.filter((_, idx) => idx !== i));

  const saveDraft = () => showToast(`Saved draft of "${name}" ${version}`);

  /* ── JSON preview derived from state ── */
  const jsonPreview = useMemo(() => {
    const payload = {
      blueprint_id: bp.id,
      name,
      version,
      document_class: bp.document_class,
      industry: bp.industry_key,
      stage: bp.status_label.toLowerCase(),
      bda_arn: bp.arn,
      description,
      fields: fields.map(f => ({
        name: f.name,
        type: f.type,
        required: f.required,
        confidence: Number((f.confidence / 100).toFixed(2)),
        validations: f.validations.map(v => ({
          rule: v.kind,
          value: v.value || undefined,
          error_message: v.error_message,
        })),
      })),
      virtual_fields: virtualFields.map(v => ({ name: v.name, type: v.type, formula: v.formula })),
      blueprint_rules: bpRules.filter(r => r.active).map(r => ({ label: r.label, detail: r.detail })),
    };
    return JSON.stringify(payload, null, 2);
  }, [bp, name, version, description, fields, virtualFields, bpRules]);

  return (
    <>
      <Head><title>Blueprint · {name} | APEX</title></Head>

      {/* Back + actions */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link href="/canvas" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: '#64748b', textDecoration: 'none' }}>
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to Canvas
        </Link>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={saveDraft}>Save Draft</button>
          <Link href="/testing" className="btn btn-secondary btn-sm">Test Extraction</Link>
          <button className="btn btn-primary btn-sm" onClick={() => setShowDeployModal(true)}>Deploy to BDA</button>
        </div>
      </div>

      {/* Header card */}
      <div className="card" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
              <input
                className="input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ fontSize: 20, fontWeight: 700, color: '#0f172a', width: 'auto', minWidth: 340, maxWidth: 480, padding: '4px 8px' }}
              />
              <input
                className="input"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                style={{ fontSize: 12, width: 90, padding: '3px 8px' }}
                title="Version"
              />
              <span className={bp.status_chip}>{bp.status_label}</span>
            </div>
            <textarea
              className="textarea"
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ fontSize: 13, color: '#64748b' }}
              placeholder="What does this blueprint extract?"
            />
            <div
              className="mono"
              style={{ fontSize: 11, color: '#64748b', marginTop: 10, background: '#f8fafc', padding: '8px 12px', borderRadius: 8, display: 'inline-block' }}
            >
              {bp.arn}
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8, fontSize: 11, color: '#94a3b8', flexWrap: 'wrap' }}>
              <span>{bp.industry_label}</span>
              {id && (<><span style={{ color: '#e2e8f0' }}>·</span><span className="mono">id: {id}</span></>)}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: '#0f172a' }}>{fields.length}</div>
            <div style={{ fontSize: 12, color: '#94a3b8' }}>Fields Mapped</div>
            <div style={{ fontSize: 11, color: avgConfidence >= 95 ? '#16a34a' : avgConfidence >= 85 ? '#d97706' : '#dc2626', fontWeight: 600, marginTop: 4 }}>
              {avgConfidence.toFixed(1)}% avg conf.
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-bar" style={{ width: 'fit-content', marginBottom: 24 }}>
        <button className={`tab ${tab === 'fields'  ? 'active' : ''}`} onClick={() => setTab('fields')}>Fields ({fields.length})</button>
        <button className={`tab ${tab === 'virtual' ? 'active' : ''}`} onClick={() => setTab('virtual')}>Virtual Fields ({virtualFields.length})</button>
        <button className={`tab ${tab === 'rules'   ? 'active' : ''}`} onClick={() => setTab('rules')}>Blueprint Rules ({bpRules.length})</button>
        <button className={`tab ${tab === 'preview' ? 'active' : ''}`} onClick={() => setTab('preview')}>JSON Preview</button>
      </div>

      {/* FIELDS tab */}
      {tab === 'fields' && (
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{
            padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            borderBottom: '1px solid #f1f5f9',
          }}>
            <span style={{ fontSize: 13, color: '#374151' }}>
              {fields.length} field{fields.length === 1 ? '' : 's'} · {avgConfidence.toFixed(1)}% avg confidence ·{' '}
              {fields.reduce((s, f) => s + f.validations.length, 0)} validation rule{fields.reduce((s, f) => s + f.validations.length, 0) === 1 ? '' : 's'}
            </span>
            <button className="btn btn-primary btn-sm" onClick={addField}>+ Add Field</button>
          </div>

          {/* Column headers */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1.8fr 2fr 1fr 90px 80px 60px 80px',
            gap: 10, padding: '10px 20px',
            background: '#f8fafc', borderBottom: '1px solid #f1f5f9',
            fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8',
          }}>
            <div>Field name</div>
            <div>Description</div>
            <div>Type</div>
            <div>Required</div>
            <div>Conf.</div>
            <div style={{ textAlign: 'center' }}>Rules</div>
            <div style={{ textAlign: 'center' }}>Actions</div>
          </div>

          {/* Rows */}
          {fields.map((f, i) => {
            const isExpanded = expandedField === f.name;
            return (
              <React.Fragment key={`${i}-${f.name}`}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1.8fr 2fr 1fr 90px 80px 60px 80px',
                  gap: 10, padding: '10px 20px', alignItems: 'center',
                  borderBottom: isExpanded ? 'none' : '1px solid #f1f5f9',
                }}>
                  <input
                    className="input mono"
                    value={f.name}
                    onChange={(e) => updateField(i, { name: e.target.value })}
                    style={{ fontSize: 13, fontWeight: 500 }}
                  />
                  <input
                    className="input"
                    value={f.desc}
                    onChange={(e) => updateField(i, { desc: e.target.value })}
                    style={{ fontSize: 12, color: '#64748b' }}
                  />
                  <select
                    className="input"
                    value={f.type}
                    onChange={(e) => updateFieldType(i, e.target.value as FieldType)}
                  >
                    {(['string','number','date','boolean','array','enum','object'] as FieldType[]).map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#374151', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={f.required}
                      onChange={(e) => updateField(i, { required: e.target.checked })}
                      style={{ accentColor: '#2563eb' }}
                    />
                    {f.required ? 'Yes' : 'No'}
                  </label>
                  <input
                    type="number" min={0} max={100} step={0.1}
                    className="input mono"
                    value={f.confidence}
                    onChange={(e) => updateField(i, { confidence: Math.max(0, Math.min(100, Number(e.target.value) || 0)) })}
                    style={{ fontSize: 12, padding: '4px 6px' }}
                    title="Confidence %"
                  />
                  <button
                    type="button"
                    onClick={() => setExpandedField(isExpanded ? null : f.name)}
                    className={f.validations.length > 0 ? 'chip-blue' : 'chip-gray'}
                    style={{ border: 'none', cursor: 'pointer', fontSize: 11 }}
                    title={isExpanded ? 'Hide validation rules' : 'Show validation rules'}
                  >
                    {f.validations.length} {isExpanded ? '▾' : '▸'}
                  </button>
                  <button
                    type="button"
                    onClick={() => removeField(i)}
                    className="btn btn-secondary btn-sm"
                    style={{ padding: '4px 10px', justifyContent: 'center' }}
                    title="Remove field"
                  >×</button>
                </div>

                {/* Inline validation-rule editor */}
                {isExpanded && (
                  <div style={{
                    padding: '16px 20px 20px',
                    background: '#f8fafc',
                    borderBottom: '1px solid #f1f5f9',
                  }}>
                    <ValidationRuleEditor
                      fieldIdx={i}
                      field={f}
                      onAdd={(kind) => addRule(i, kind)}
                      onUpdate={(ri, patch) => updateRule(i, ri, patch)}
                      onRemove={(ri) => removeRule(i, ri)}
                    />
                  </div>
                )}
              </React.Fragment>
            );
          })}

          {fields.length === 0 && (
            <div style={{ padding: 32, textAlign: 'center', fontSize: 13, color: '#94a3b8' }}>
              No fields yet. Click <strong>+ Add Field</strong> above to start mapping the schema.
            </div>
          )}
        </div>
      )}

      {/* VIRTUAL FIELDS tab */}
      {tab === 'virtual' && (
        <div className="card" style={{ padding: 24, maxWidth: 820 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>
              Virtual / Computed Fields
            </div>
            <button className="btn btn-primary btn-sm" onClick={addVirtual}>+ Add Virtual Field</button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {virtualFields.map((v, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1.5fr 3fr 110px 40px', gap: 10, alignItems: 'center' }}>
                <input
                  className="input mono"
                  value={v.name}
                  onChange={(e) => updateVirtual(i, { name: e.target.value })}
                  style={{ fontSize: 13, fontWeight: 500 }}
                />
                <input
                  className="input mono"
                  value={v.formula}
                  onChange={(e) => updateVirtual(i, { formula: e.target.value })}
                  placeholder="e.g. due_date - invoice_date"
                  style={{ fontSize: 12, color: '#64748b' }}
                />
                <select
                  className="input"
                  value={v.type}
                  onChange={(e) => updateVirtual(i, { type: e.target.value as FieldType })}
                >
                  {(['string','number','date','boolean','array','enum','object'] as FieldType[]).map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <button className="btn btn-secondary btn-sm" onClick={() => removeVirtual(i)} style={{ padding: '4px 10px' }}>×</button>
              </div>
            ))}
            {virtualFields.length === 0 && (
              <div style={{ fontSize: 12, color: '#94a3b8' }}>No virtual fields yet.</div>
            )}
          </div>
        </div>
      )}

      {/* BLUEPRINT RULES tab */}
      {tab === 'rules' && (
        <div className="card" style={{ padding: 24, maxWidth: 820 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>
              Blueprint-wide Rules
            </div>
            <button className="btn btn-primary btn-sm" onClick={addBpRule}>+ Add Rule</button>
          </div>

          <div style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>
            Rules that apply to the whole document (duplicate checks, cross-field validation, etc.).
            For rules on a single field, use the per-field editor on the <strong>Fields</strong> tab.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {bpRules.map((r, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1.2fr 3fr 110px 40px', gap: 10, alignItems: 'center' }}>
                <input
                  className="input"
                  value={r.label}
                  onChange={(e) => updateBpRule(i, { label: e.target.value })}
                  style={{ fontSize: 13, fontWeight: 500 }}
                />
                <input
                  className="input"
                  value={r.detail}
                  onChange={(e) => updateBpRule(i, { detail: e.target.value })}
                  style={{ fontSize: 12, color: '#64748b' }}
                />
                <button
                  className={r.active ? 'chip-green' : 'chip-gray'}
                  onClick={() => updateBpRule(i, { active: !r.active })}
                  style={{ border: 'none', cursor: 'pointer' }}
                >
                  {r.active ? 'Active' : 'Inactive'}
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => removeBpRule(i)} style={{ padding: '4px 10px' }}>×</button>
              </div>
            ))}
            {bpRules.length === 0 && (
              <div style={{ fontSize: 12, color: '#94a3b8' }}>No blueprint rules yet.</div>
            )}
          </div>
        </div>
      )}

      {/* JSON PREVIEW tab */}
      {tab === 'preview' && (
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>BDA Schema · live</div>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                navigator.clipboard?.writeText(jsonPreview);
                showToast('JSON copied to clipboard');
              }}
            >Copy</button>
          </div>
          <div style={{ background: '#0d1117', borderRadius: 12, padding: 20, overflowX: 'auto', maxHeight: '60vh' }}>
            <pre className="mono" style={{ fontSize: 12, color: '#e6edf3', margin: 0 }}>{jsonPreview}</pre>
          </div>
        </div>
      )}

      {/* Deploy modal */}
      {showDeployModal && (
        <div className="modal-overlay" onClick={() => setShowDeployModal(false)}>
          <div className="modal" style={{ padding: 28 }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>Deploy to Bedrock Data Automation</h3>
            <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
              Creates a new version of this blueprint in BDA. {fields.length} fields · {fields.reduce((s, f) => s + f.validations.length, 0)} validation rules.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setShowDeployModal(false)}>Cancel</button>
              <button
                className="btn btn-primary"
                onClick={() => { setShowDeployModal(false); showToast(`Deployed ${name} ${version} to BDA`); }}
              >Deploy</button>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 20, right: 24, zIndex: 200,
          background: '#064e3b', color: '#ecfdf5', padding: '10px 16px',
          borderRadius: 8, fontSize: 13, boxShadow: '0 10px 30px rgba(2,6,23,.25)',
        }}>
          ✓ {toast}
        </div>
      )}
    </>
  );
}

/* ═════════════════════ per-field rule editor ═════════════════════ */

function ValidationRuleEditor({
  field, onAdd, onUpdate, onRemove,
}: {
  fieldIdx: number;
  field: Field;
  onAdd: (kind: RuleKind) => void;
  onUpdate: (ri: number, patch: Partial<ValidationRule>) => void;
  onRemove: (ri: number) => void;
}) {
  const available = applicableRuleKinds(field.type);
  const [picker, setPicker] = useState<RuleKind>(available[0] ?? 'required');

  // Keep picker valid when field type changes
  useEffect(() => {
    if (!available.includes(picker)) setPicker(available[0] ?? 'required');
  }, [field.type, available, picker]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10, flexWrap: 'wrap', gap: 10 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: '#334155' }}>
          Validation Rules for <span className="mono">{field.name}</span>
          <span style={{ color: '#94a3b8', fontWeight: 400 }}> · {field.validations.length} rule{field.validations.length === 1 ? '' : 's'}</span>
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <select
            className="input"
            value={picker}
            onChange={(e) => setPicker(e.target.value as RuleKind)}
            style={{ width: 180, fontSize: 12 }}
          >
            {available.map((k) => (
              <option key={k} value={k}>{RULE_LABEL[k]}</option>
            ))}
          </select>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => onAdd(picker)}
          >+ Add Rule</button>
        </div>
      </div>

      {field.validations.length === 0 && (
        <div style={{ fontSize: 12, color: '#94a3b8', padding: 8 }}>
          No validation rules on this field yet. Pick a rule type above and click <strong>+ Add Rule</strong>.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {field.validations.map((r, ri) => {
          const meta = RULE_TYPES.find((m) => m.kind === r.kind)!;
          const takesValue = r.kind !== 'required';
          return (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns: '140px 1fr 1.2fr 40px',
                gap: 10,
                padding: '10px 12px',
                background: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: 10,
                alignItems: 'center',
              }}
            >
              <div style={{ fontSize: 12, fontWeight: 600, color: '#1d4ed8' }}>{meta.label}</div>
              <input
                className="input mono"
                value={r.value}
                disabled={!takesValue}
                onChange={(e) => onUpdate(ri, { value: e.target.value })}
                placeholder={meta.hint}
                style={{ fontSize: 12, opacity: takesValue ? 1 : 0.55 }}
              />
              <input
                className="input"
                value={r.error_message}
                onChange={(e) => onUpdate(ri, { error_message: e.target.value })}
                placeholder="Error message shown to reviewer"
                style={{ fontSize: 12 }}
              />
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => onRemove(ri)}
                style={{ padding: '4px 10px' }}
                title="Remove rule"
              >×</button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═════════════════════ lookup + data ═════════════════════ */

/** Empty skeleton rendered while the API call is in-flight. NEVER fall through
 *  to an invoice/CBB hardcoded shape during loading — that's the bug we just
 *  fixed. See aws/CLAUDE.md "No hardcoding" rule. */
const EMPTY_BLUEPRINT: BlueprintData = {
  id: '',
  name: 'Loading…',
  version: '—',
  description: '',
  industry_label: '',
  status_label: 'Loading',
  status_chip: 'chip-gray',
  arn: '',
  document_class: '',
  industry_key: '',
  fields: [],
  virtual_fields: [],
  blueprint_rules: [],
};

/**
 * Coerce a backend Blueprint row → the rich BlueprintData shape this page
 * renders. Backend shape (see aws/backend/models/blueprint.py + the seeded
 * blueprint JSON files in aws/blueprints/<industry>/) is roughly:
 *   { blueprint_id, name, description, industry, document_type, version,
 *     bdaSchema: { fields: { <name>: { type, description, required, ... } } } }
 *
 * The bdaSchema.fields is a DICT (not array), keyed by field name. We
 * convert it to the array shape this page expects.
 */
function _apiToBlueprintData(api: any): BlueprintData {
  if (!api) return EMPTY_BLUEPRINT;

  const industryKey = (api.industry || '').toLowerCase();
  const industryLabel = (() => {
    if (industryKey === 'nuclear_operations')    return 'Nuclear Operations & Reliability';
    if (industryKey === 'telecommunications')    return 'Telecommunications';
    if (industryKey === 'supply_manufacturing'
     || industryKey === 'manufacturing'
     || industryKey === 'supply_chain')          return 'Supply Chain & Manufacturing';
    if (industryKey === 'financial_services')    return 'Financial Services';
    if (industryKey === 'insurance_underwriting')return 'Commercial Insurance';
    if (industryKey.startsWith('healthcare'))    return 'Healthcare';
    if (industryKey === 'aerospace_defense')     return 'Aerospace & Defense';
    if (!industryKey) return '';
    return industryKey.split('_').map((s: string) => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
  })();

  // Backend returns fields under `schema_fields: [{name, type, description, required}, …]`
  // (flattened by the seeder from any of: bdaSchema.fields / bdaSchema.properties /
  // top-level JSON-Schema properties / direct schema_fields).
  // Tolerate the older nested shapes too in case some legacy rows still exist.
  const rawFields =
    api?.schema_fields                     // canonical (post-seeder)
    ?? api?.bdaSchema?.fields              // legacy BDA wrapper
    ?? api?.schema?.properties             // legacy JSON Schema wrapper
    ?? api?.fields                          // ad-hoc
    ?? [];
  const fields: Field[] = (() => {
    if (Array.isArray(rawFields)) {
      return rawFields.map((f: any): Field => ({
        name:        f.name || '(unnamed)',
        desc:        f.description || '',
        type:        (f.type || 'string') as Field['type'],
        confidence:  typeof f.confidence === 'number' ? f.confidence : 95,
        required:    !!f.required,
        validations: [],
      }));
    }
    return Object.entries(rawFields).map(([name, spec]: [string, any]): Field => ({
      name,
      desc:        spec?.description || '',
      type:        (spec?.type || 'string') as Field['type'],
      confidence:  typeof spec?.confidence === 'number' ? spec.confidence : 95,
      required:    !!spec?.required,
      validations: [],
    }));
  })();

  const status = (api.status || 'draft').toLowerCase();
  const statusChipMap: Record<string, string> = {
    deployed: 'chip-green', active: 'chip-green',
    draft:    'chip-gray',  archived: 'chip-red',
  };

  return {
    id:             api.blueprint_id || api.id || '',
    name:           humanizeName(api.name) || api.name || '(unnamed blueprint)',
    version:        api.version || api?.bdaSchema?.version || 'v1.0',
    description:    api.description || api?.bdaSchema?.description || '',
    industry_label: industryLabel,
    status_label:   status.charAt(0).toUpperCase() + status.slice(1),
    status_chip:    statusChipMap[status] || 'chip-gray',
    arn:            api.arn || '',
    document_class: api.document_type || api?.bdaSchema?.documentClass || '',
    industry_key:   industryKey,
    fields,
    // Backend doesn't carry virtual_fields / blueprint_rules — leave empty
    // rather than synthesise. Tabs render their own empty states.
    virtual_fields:   [],
    blueprint_rules:  [],
  };
}

function lookupBlueprint(id: string): BlueprintData {
  // Lookup order: CBB → STP → Telecom → safe "not found" stub.
  // Per the CLAUDE.md ZERO-HARDCODING RULE, unknown ids MUST NOT fall
  // through to invoice content. Render an explicit "not found" stub instead
  // so the user sees the truth rather than mis-attributed content.
  return CBB_BLUEPRINT_DATA[id]
      ?? STP_BLUEPRINT_DATA[id]
      ?? TELCO_BLUEPRINT_DATA[id]
      ?? EPROD_BLUEPRINT_DATA[id]
      ?? DEFAULT_BLUEPRINT;
}

const CBB_BLUEPRINT_DATA: Record<string, BlueprintData> = {
  'bp-cbb-order': {
    id: 'bp-cbb-order',
    name: 'Order Modification Form v2.1',
    version: 'v2.1',
    description: 'Parses distributor-submitted order-modification PDFs. Extracts order ID, original + requested dimensions, product SKU, quantity, contact info, and reason.',
    industry_label: 'Supply Chain & Manufacturing · CBB',
    industry_key: 'supply_manufacturing',
    document_class: 'order_modification',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/order-mod-v2.1',
    fields: [
      { name: 'order_id', desc: 'CBB order identifier', type: 'string', confidence: 99.8, required: true, validations: [
        { id: 'r1',  kind: 'required', value: '',                           error_message: 'order_id is required.' },
        { id: 'r2',  kind: 'regex',    value: '^CBB-ORD-\\d{4,8}$',          error_message: 'Must match CBB-ORD-NNNN format.' },
      ]},
      { name: 'original_dimensions.width_in', desc: 'Original width (inches)', type: 'number', confidence: 98.2, required: true, validations: [
        { id: 'r3',  kind: 'min', value: '6',   error_message: 'Width below 6" is not a valid product size.' },
        { id: 'r4',  kind: 'max', value: '144', error_message: 'Width above 144" exceeds product catalog.' },
      ]},
      { name: 'original_dimensions.height_in', desc: 'Original height (inches)', type: 'number', confidence: 98.1, required: true, validations: [
        { id: 'r5',  kind: 'min', value: '6',   error_message: 'Height below 6" is not a valid product size.' },
        { id: 'r6',  kind: 'max', value: '144', error_message: 'Height above 144" exceeds product catalog.' },
      ]},
      { name: 'requested_dimensions.width_in', desc: 'Requested width (inches)', type: 'number', confidence: 97.6, required: true, validations: [
        { id: 'r7',  kind: 'min',    value: '6',   error_message: 'Width below 6" is not a valid product size.' },
        { id: 'r8',  kind: 'max',    value: '144', error_message: 'Width above 144" exceeds product catalog.' },
        { id: 'r9',  kind: 'custom', value: 'abs(requested_dimensions.width_in - original_dimensions.width_in) / original_dimensions.width_in <= 0.05',
          error_message: 'Requested width exceeds 5% tolerance — route to Customer Ops review.' },
      ]},
      { name: 'requested_dimensions.height_in', desc: 'Requested height (inches)', type: 'number', confidence: 97.4, required: true, validations: [
        { id: 'r10', kind: 'min',    value: '6',   error_message: 'Height below 6" is not a valid product size.' },
        { id: 'r11', kind: 'max',    value: '144', error_message: 'Height above 144" exceeds product catalog.' },
        { id: 'r12', kind: 'custom', value: 'abs(requested_dimensions.height_in - original_dimensions.height_in) / original_dimensions.height_in <= 0.05',
          error_message: 'Requested height exceeds 5% tolerance — route to Customer Ops review.' },
      ]},
      { name: 'distributor_name', desc: 'Name of distributor', type: 'string', confidence: 99.1, required: true, validations: [
        { id: 'r13', kind: 'min_length', value: '2', error_message: 'Distributor name is too short.' },
      ]},
      { name: 'distributor_id', desc: 'CBB distributor ID', type: 'string', confidence: 96.2, required: false, validations: [] },
      { name: 'product_sku',    desc: 'Product SKU', type: 'string', confidence: 96.8, required: true, validations: [
        { id: 'r14', kind: 'regex', value: '^[A-Z]{3}-\\d{4}-[A-Z]{2}$', error_message: 'SKU must match <AAA>-<NNNN>-<AA>.' },
      ]},
      { name: 'quantity', desc: 'Units ordered', type: 'number', confidence: 99.4, required: true, validations: [
        { id: 'r15', kind: 'min', value: '1',     error_message: 'Quantity must be at least 1.' },
        { id: 'r16', kind: 'max', value: '10000', error_message: 'Quantity exceeds bulk order limit.' },
      ]},
      { name: 'requested_delivery_date', desc: 'Requested delivery date', type: 'date', confidence: 94.3, required: false, validations: [
        { id: 'r17', kind: 'date_range', value: '2026-04-21..', error_message: 'Delivery date must not be in the past.' },
      ]},
      { name: 'reason',        desc: 'Free-text modification reason', type: 'string', confidence: 89.7, required: false, validations: [
        { id: 'r18', kind: 'max_length', value: '2000', error_message: 'Keep reason under 2000 characters.' },
      ]},
      { name: 'contact_email', desc: 'Distributor contact email', type: 'string', confidence: 98.6, required: true, validations: [
        { id: 'r19', kind: 'regex', value: '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$', error_message: 'Provide a valid email address.' },
      ]},
    ],
    virtual_fields: [
      { name: 'width_delta_pct',  formula: 'abs(requested_dimensions.width_in - original_dimensions.width_in) / original_dimensions.width_in',   type: 'number' },
      { name: 'height_delta_pct', formula: 'abs(requested_dimensions.height_in - original_dimensions.height_in) / original_dimensions.height_in', type: 'number' },
      { name: 'auto_approvable',  formula: 'width_delta_pct <= 0.05 AND height_delta_pct <= 0.05',                                               type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Tolerance gate',     detail: 'Both width_delta_pct and height_delta_pct must be ≤ 0.05 for auto-approval.', active: true },
      { label: 'Production guard',   detail: 'Block modification if original_order.production_status == "STARTED".',        active: true },
      { label: 'Duplicate modifiers',detail: 'No two modifications on the same order_id within 24 hours.',                  active: true },
    ],
  },

  'bp-cbb-qc': {
    id: 'bp-cbb-qc',
    name: 'QC Certificate v3.0',
    version: 'v3.0',
    description: 'Supplier QC certificate schema covering lot identity, material, supplier, inspection data, tensile + color measurements, and pass/fail status.',
    industry_label: 'Supply Chain & Manufacturing · CBB',
    industry_key: 'supply_manufacturing',
    document_class: 'qc_certificate',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/qc-cert-v3.0',
    fields: [
      { name: 'lot_id',            desc: 'Lot identifier',          type: 'string', confidence: 99.9, required: true, validations: [
        { id: 'q1', kind: 'regex', value: '^LOT-[AB]\\d{2}$', error_message: 'Lot IDs follow LOT-[A|B]NN.' },
      ]},
      { name: 'material',          desc: 'Material description',     type: 'string', confidence: 99.4, required: true, validations: [] },
      { name: 'supplier_name',     desc: 'Supplier name',            type: 'string', confidence: 99.2, required: true, validations: [] },
      { name: 'supplier_id',       desc: 'Supplier registry ID',     type: 'string', confidence: 98.7, required: true, validations: [
        { id: 'q2', kind: 'regex', value: '^SUP-\\d{4}$', error_message: 'Must match SUP-NNNN.' },
      ]},
      { name: 'batch_id',          desc: 'Supplier batch ID',        type: 'string', confidence: 99.1, required: true, validations: [] },
      { name: 'inspection_date',   desc: 'Date of inspection',       type: 'date',   confidence: 99.3, required: true, validations: [] },
      { name: 'inspector_id',      desc: 'Inspector ID',             type: 'string', confidence: 97.4, required: true, validations: [] },
      { name: 'tensile_strength',  desc: 'Measured tensile (MPa)',   type: 'number', confidence: 99.6, required: true, validations: [
        { id: 'q3', kind: 'min', value: '0',   error_message: 'Tensile must be ≥ 0.' },
        { id: 'q4', kind: 'max', value: '200', error_message: 'Tensile above 200 MPa is out of plausible range.' },
      ]},
      { name: 'tensile_spec_min',  desc: 'Spec minimum tensile',     type: 'number', confidence: 99.8, required: true, validations: [] },
      { name: 'color_delta_e',     desc: 'Color variance (ΔE)',      type: 'number', confidence: 98.9, required: true, validations: [
        { id: 'q5', kind: 'min', value: '0', error_message: 'ΔE must be ≥ 0.' },
        { id: 'q6', kind: 'max', value: '5', error_message: 'ΔE above 5 is out of plausible range.' },
      ]},
      { name: 'color_threshold',   desc: 'Spec color threshold',     type: 'number', confidence: 99.2, required: true, validations: [] },
      { name: 'moisture_pct',      desc: 'Moisture %',               type: 'number', confidence: 97.1, required: false, validations: [
        { id: 'q7', kind: 'min', value: '0',  error_message: 'Moisture must be ≥ 0%.' },
        { id: 'q8', kind: 'max', value: '15', error_message: 'Moisture above 15% flags a material handling issue.' },
      ]},
      { name: 'density_gcm3',      desc: 'Density (g/cm³)',          type: 'number', confidence: 96.8, required: false, validations: [] },
      { name: 'quantity_kg',       desc: 'Lot mass (kg)',            type: 'number', confidence: 99.4, required: true, validations: [
        { id: 'q9', kind: 'min', value: '1', error_message: 'Quantity must be at least 1 kg.' },
      ]},
      { name: 'unit_price_usd',    desc: 'USD per unit',             type: 'number', confidence: 98.6, required: true, validations: [
        { id: 'q10', kind: 'min', value: '0', error_message: 'Price must be ≥ 0.' },
      ]},
      { name: 'plant_destination', desc: 'Destination plant',        type: 'string', confidence: 98.3, required: true, validations: [] },
      { name: 'pass_fail',         desc: 'Overall result',           type: 'enum',   confidence: 99.9, required: true, validations: [
        { id: 'q11', kind: 'enum_values', value: 'PASS,FAIL', error_message: 'Must be PASS or FAIL.' },
      ]},
      { name: 'variance_pct',      desc: 'Variance vs spec (%)',     type: 'number', confidence: 99.1, required: true, validations: [] },
    ],
    virtual_fields: [
      { name: 'tensile_passes', formula: 'tensile_strength >= tensile_spec_min', type: 'boolean' },
      { name: 'color_passes',   formula: 'color_delta_e <= color_threshold',     type: 'boolean' },
      { name: 'lot_value_usd',  formula: 'quantity_kg * unit_price_usd',         type: 'number'  },
    ],
    blueprint_rules: [
      { label: 'Tolerance gate',   detail: 'tensile_passes AND color_passes must both be true for auto-clear.', active: true },
      { label: 'Hold threshold',   detail: 'If any lot fails, generate partial_hold for that lot only.',         active: true },
      { label: 'Quarantine alert', detail: 'Notify plant manager when total held value > $10,000.',              active: true },
    ],
  },

  'bp-cbb-disrupt': {
    id: 'bp-cbb-disrupt',
    name: 'Supplier Delay Alert v1.0',
    version: 'v1.0',
    description: 'Parses GSM XML alerts (port strikes, supplier delays, natural disasters).',
    industry_label: 'Supply Chain & Manufacturing · CBB',
    industry_key: 'supply_manufacturing',
    document_class: 'supplier_alert',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/supplier-alert-v1.0',
    fields: [
      { name: 'alert_id',          desc: 'GSM alert ID',             type: 'string', confidence: 99.9, required: true, validations: [
        { id: 'd1', kind: 'regex', value: '^SC-ALERT-\\d{4}-\\d{4}$', error_message: 'Must match SC-ALERT-YYYY-NNNN.' },
      ]},
      { name: 'event_type',        desc: 'Type of disruption',       type: 'enum',   confidence: 99.6, required: true, validations: [
        { id: 'd2', kind: 'enum_values', value: 'PortStrike,SupplierDelay,Weather,NaturalDisaster,Other', error_message: 'Unknown event type.' },
      ]},
      { name: 'port',              desc: 'Affected port',            type: 'string', confidence: 99.1, required: true, validations: [] },
      { name: 'affected_supplier', desc: 'Supplier name',            type: 'string', confidence: 99.3, required: true, validations: [] },
      { name: 'supplier_id',       desc: 'Supplier registry ID',     type: 'string', confidence: 98.8, required: true, validations: [] },
      { name: 'material',          desc: 'Material impacted',        type: 'string', confidence: 99.2, required: true, validations: [] },
      { name: 'material_grade',    desc: 'Grade / classification',   type: 'string', confidence: 97.4, required: false, validations: [] },
      { name: 'delay_days',        desc: 'Expected delay (days)',    type: 'number', confidence: 98.9, required: true, validations: [
        { id: 'd3', kind: 'min', value: '0', error_message: 'Delay cannot be negative.' },
      ]},
      { name: 'severity',          desc: 'Severity level',           type: 'enum',   confidence: 99.7, required: true, validations: [
        { id: 'd4', kind: 'enum_values', value: 'LOW,MEDIUM,HIGH,CRITICAL', error_message: 'Severity must be LOW/MEDIUM/HIGH/CRITICAL.' },
      ]},
      { name: 'alert_timestamp',   desc: 'Alert creation time',      type: 'date',   confidence: 99.8, required: true, validations: [] },
      { name: 'expected_recovery', desc: 'Expected recovery date',   type: 'date',   confidence: 96.2, required: false, validations: [] },
      { name: 'source_confidence', desc: 'Alert source confidence',  type: 'number', confidence: 99.5, required: true, validations: [
        { id: 'd5', kind: 'min', value: '0', error_message: 'Confidence must be ≥ 0.' },
        { id: 'd6', kind: 'max', value: '1', error_message: 'Confidence must be ≤ 1.' },
      ]},
      { name: 'region',            desc: 'Affected region',          type: 'string', confidence: 98.7, required: true, validations: [] },
      { name: 'notes',             desc: 'Free-text notes',          type: 'string', confidence: 91.4, required: false, validations: [
        { id: 'd7', kind: 'max_length', value: '5000', error_message: 'Keep notes under 5000 characters.' },
      ]},
    ],
    virtual_fields: [
      { name: 'is_critical', formula: 'severity == "CRITICAL" OR severity == "HIGH"', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Escalation gate',     detail: 'Escalate to Supply Chain Director when value_at_risk_usd > $500,000.', active: true },
      { label: 'Confidence threshold',detail: 'Drop alerts with source_confidence < 0.85.',                           active: true },
    ],
  },
};

// ─────────────────────── STP · Nuclear Operations blueprints ───────────────────────
// 6 blueprints used by ChatSTP UC-1..4 playbooks. Mirror the JSON on disk
// under blueprints/nuclear_operations/.

const STP_BLUEPRINT_DATA: Record<string, BlueprintData> = {
  'bp-stp-hr-policy': {
    id: 'bp-stp-hr-policy',
    name: 'STP HR Policy Document',
    version: 'v1.0',
    description: 'Extracts policy id, effective date, applicability, and obligations from STP HR / training / qualification policy PDFs.',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'hr_policy',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/hr-policy-v1',
    fields: [
      { name: 'policy_id',         desc: 'Policy identifier (e.g. STP-HR-POL-014)', type: 'string', confidence: 99.8, required: true,  validations: [
        { id: 's1', kind: 'regex',    value: '^STP-[A-Z]{2,4}-[A-Z]{3,4}-\\d{2,4}$', error_message: 'Must match STP-XX-YYY-NNNN.' },
      ]},
      { name: 'revision',          desc: 'Policy revision',                      type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'effective_date',    desc: 'Effective date',                       type: 'date',   confidence: 98.7, required: true,  validations: [] },
      { name: 'expiration_date',   desc: 'Next review / expiration date',         type: 'date',   confidence: 95.1, required: false, validations: [] },
      { name: 'applicability',     desc: 'Job roles / groups the policy applies to', type: 'array', confidence: 97.2, required: true,  validations: [] },
      { name: 'obligations',       desc: 'List of obligations',                  type: 'array',  confidence: 94.8, required: true,  validations: [] },
      { name: 'training_hours',    desc: 'Required training hours',              type: 'number', confidence: 96.1, required: false, validations: [
        { id: 's2', kind: 'min',  value: '0', error_message: 'Training hours cannot be negative.' },
      ]},
      { name: 'approver',          desc: 'Approving authority (e.g. SRO, HR-Director)', type: 'string', confidence: 98.4, required: true,  validations: [] },
    ],
    virtual_fields: [],
    blueprint_rules: [
      { label: 'Required citation', detail: 'Every policy answer must cite the policy_id + revision.', active: true },
    ],
  },

  'bp-stp-procedure': {
    id: 'bp-stp-procedure',
    name: 'STP Plant Procedure',
    version: 'v1.0',
    description: 'Parses STP operating, surveillance, abnormal, and emergency procedures (STP-OP-*, STP-SP-*, STP-AOP-*, STP-EOP-*).',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'plant_procedure',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/procedure-v1',
    fields: [
      { name: 'procedure_id',      desc: 'STP procedure id (e.g. STP-OP-2204)', type: 'string', confidence: 100,  required: true,  validations: [] },
      { name: 'revision',          desc: 'Procedure revision (Rev 6, …)',       type: 'string', confidence: 99.8, required: true,  validations: [] },
      { name: 'title',             desc: 'Procedure title',                      type: 'string', confidence: 99.6, required: true,  validations: [] },
      { name: 'procedure_type',    desc: 'OP / SP / AOP / EOP',                  type: 'enum',   confidence: 99.4, required: true,  validations: [
        { id: 'p1', kind: 'enum_values', value: 'OP,SP,AOP,EOP,GP,CP', error_message: 'Procedure type must be one of OP/SP/AOP/EOP/GP/CP.' },
      ]},
      { name: 'sections',          desc: 'Numbered sections + step bodies',      type: 'array',  confidence: 98.7, required: true,  validations: [] },
      { name: 'lco_references',    desc: 'Tech Spec LCO references',             type: 'array',  confidence: 96.4, required: false, validations: [] },
      { name: 'allowed_outage_time', desc: 'AOT (e.g. 72h, 7d)',                 type: 'string', confidence: 97.1, required: false, validations: [] },
      { name: 'mode_applicability',  desc: 'Plant modes the procedure applies in',type: 'array', confidence: 98.8, required: true,  validations: [] },
      { name: 'sign_off_chain',    desc: 'Required signatures',                  type: 'array',  confidence: 95.2, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'is_safety_related', formula: 'procedure_type IN ("OP","EOP","AOP") AND lco_references.length > 0', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Citation gate',    detail: 'Every operator-facing answer must quote section + step verbatim.', active: true },
      { label: 'LCO surfacing',    detail: 'When lco_references is non-empty, surface AOT in the answer.',     active: true },
    ],
  },

  'bp-stp-work-order': {
    id: 'bp-stp-work-order',
    name: 'STP Work Order Record',
    version: 'v1.0',
    description: 'Parses STP work order records from Oracle PMHISTORY. Captures equipment_id, work_type, performed_by, dates, parts used, post-maintenance test results, and attachment references.',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'work_order',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-order-v1',
    fields: [
      { name: 'work_order_id',     desc: 'WO id (e.g. WO-2026-00871)',  type: 'string', confidence: 100,  required: true,  validations: [
        { id: 'w1', kind: 'regex', value: '^WO-\\d{4}-\\d{4,6}$', error_message: 'Must match WO-YYYY-NNNN.' },
      ]},
      { name: 'equipment_id',      desc: 'Equipment tag (e.g. P-3A)',  type: 'string', confidence: 99.8, required: true,  validations: [] },
      { name: 'work_type',         desc: 'PM / CM / PdM / IM',          type: 'enum',   confidence: 98.4, required: true,  validations: [
        { id: 'w2', kind: 'enum_values', value: 'PM,CM,PdM,IM,IST', error_message: 'work_type must be PM/CM/PdM/IM/IST.' },
      ]},
      { name: 'performed_by',      desc: 'Engineer initials (joined to personnel)', type: 'string', confidence: 96.7, required: true,  validations: [] },
      { name: 'start_date',        desc: 'Work order start date',       type: 'date',   confidence: 99.2, required: true,  validations: [] },
      { name: 'completion_date',   desc: 'Work order completion date',  type: 'date',   confidence: 99.2, required: true,  validations: [] },
      { name: 'duration_hours',    desc: 'Actual duration (hours)',     type: 'number', confidence: 95.4, required: false, validations: [
        { id: 'w3', kind: 'min', value: '0', error_message: 'Duration cannot be negative.' },
      ]},
      { name: 'parts_consumed',    desc: 'List of parts used',          type: 'array',  confidence: 93.7, required: false, validations: [] },
      { name: 'pmt_result',        desc: 'Post-maintenance test result',type: 'enum',   confidence: 97.8, required: true,  validations: [
        { id: 'w4', kind: 'enum_values', value: 'PASS,FAIL,NA', error_message: 'pmt_result must be PASS / FAIL / NA.' },
      ]},
      { name: 'attachment_refs',   desc: 'Scanned WP attachment S3 refs', type: 'array', confidence: 94.1, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'time_to_close_d', formula: 'completion_date - start_date', type: 'number' },
    ],
    blueprint_rules: [
      { label: 'PMT closure',  detail: 'Work orders cannot close without a PMT result entry.', active: true },
    ],
  },

  'bp-stp-work-package': {
    id: 'bp-stp-work-package',
    name: 'STP Scanned Work Package',
    version: 'v1.0',
    description: 'OCR + structured extraction from scanned STP work packages. Captures equipment_id, failure mode codes, narrative description, LOTO sign-offs, parts list, post-maintenance test results, and the responsible engineer.',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'work_package',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-package-v1',
    fields: [
      { name: 'wp_id',                desc: 'Work package id',                type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'equipment_id',         desc: 'Equipment tag (e.g. P-3A)',      type: 'string', confidence: 98.7, required: true,  validations: [] },
      { name: 'failure_mode',         desc: 'Failure mode classifier label',  type: 'string', confidence: 92.1, required: true,  validations: [] },
      { name: 'narrative',            desc: 'Free-text failure narrative',     type: 'string', confidence: 94.4, required: true,  validations: [] },
      { name: 'loto_steps',           desc: 'LOTO sequence (boundary list)',   type: 'array',  confidence: 89.7, required: false, validations: [] },
      { name: 'parts_consumed',       desc: 'Parts used in the repair',        type: 'array',  confidence: 91.4, required: false, validations: [] },
      { name: 'pmt_result',           desc: 'Post-maintenance test result',    type: 'enum',   confidence: 96.2, required: true,  validations: [] },
      { name: 'engineer_initials',    desc: 'Responsible engineer initials',   type: 'string', confidence: 95.4, required: true,  validations: [] },
    ],
    virtual_fields: [],
    blueprint_rules: [
      { label: 'Failure code present', detail: 'Every work package must classify a failure_mode before close.', active: true },
    ],
  },

  'bp-stp-incident': {
    id: 'bp-stp-incident',
    name: 'STP Incident / CR Report',
    version: 'v1.0',
    description: 'Extracts data from STP Condition Reports (CR-YYYY-NNNN). Captures severity, timeline, root cause analysis status, CAR linkage, and recurrence indicator.',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'condition_report',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/incident-v1',
    fields: [
      { name: 'cr_id',                 desc: 'Condition Report id',          type: 'string', confidence: 99.8, required: true,  validations: [] },
      { name: 'severity',              desc: 'Significance level',            type: 'enum',   confidence: 98.4, required: true,  validations: [
        { id: 'c1', kind: 'enum_values', value: 'A,B,C,D', error_message: 'Severity must be A/B/C/D per STP CAP procedure.' },
      ]},
      { name: 'equipment_id',          desc: 'Equipment involved',            type: 'string', confidence: 97.1, required: false, validations: [] },
      { name: 'timeline_events',       desc: 'Sequence of events',            type: 'array',  confidence: 93.4, required: true,  validations: [] },
      { name: 'root_cause_analysis_status', desc: 'RCA status',               type: 'enum',   confidence: 96.7, required: true,  validations: [] },
      { name: 'cars_linked',           desc: 'Corrective Action Requests',    type: 'array',  confidence: 95.8, required: false, validations: [] },
      { name: 'recurrence_check',      desc: 'Recurrence detection signal',   type: 'boolean',confidence: 94.2, required: true,  validations: [] },
      { name: 'prior_crs',             desc: 'Cross-referenced prior CRs',    type: 'array',  confidence: 92.1, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'is_recurring', formula: 'prior_crs.length > 0', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Recurrence escalation', detail: 'CRs with prior_crs ≥ 3 escalate to (a)(1) MR review.', active: true },
    ],
  },

  'bp-stp-sensor': {
    id: 'bp-stp-sensor',
    name: 'STP Sensor Telemetry Schema',
    version: 'v1.0',
    description: 'Schema for sensor telemetry streams used by ApexSignal (vibration, oil analysis, thermography, process trends).',
    industry_label: 'Nuclear Operations & Reliability · STP',
    industry_key: 'nuclear_operations',
    document_class: 'sensor_telemetry',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/sensor-v1',
    fields: [
      { name: 'equipment_id', desc: 'Equipment tag',                       type: 'string', confidence: 99.9, required: true,  validations: [] },
      { name: 'sensor_type',  desc: 'vibration / oil / thermo / process', type: 'enum',   confidence: 99.8, required: true,  validations: [
        { id: 't1', kind: 'enum_values', value: 'vibration,oil,thermography,process,pressure,flow', error_message: 'Unsupported sensor_type.' },
      ]},
      { name: 'timestamp',    desc: 'ISO-8601 timestamp',                  type: 'date',   confidence: 99.9, required: true,  validations: [] },
      { name: 'value',        desc: 'Reading value',                       type: 'number', confidence: 99.8, required: true,  validations: [] },
      { name: 'unit',         desc: 'Unit of measurement (mils, ppm, °F)', type: 'string', confidence: 99.7, required: true,  validations: [] },
      { name: 'baseline',     desc: 'Configured baseline / setpoint',      type: 'number', confidence: 97.4, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'delta_pct', formula: '(value - baseline) / baseline', type: 'number' },
    ],
    blueprint_rules: [
      { label: 'Drift guard', detail: 'delta_pct above 0.25 fires an anomaly_detect event for the equipment.', active: true },
    ],
  },
};

// ─────────────────────── Telecommunications · Verizon Far Edge blueprints ───────────────────────
// 5 blueprints mirror the JSON on disk under blueprints/telecommunications/.

const TELCO_BLUEPRINT_DATA: Record<string, BlueprintData> = {
  'bp-tel-robot': {
    id: 'bp-tel-robot',
    name: 'ROBOT Framework Test Output',
    version: 'v1.0',
    description: 'Parses Verizon Far Edge ROBOT Framework XML output (~100 KB · 247 tests per cycle). Surfaces test_case, status, library, message, and suite-level totals for CertificationAgent.',
    industry_label: 'Telecommunications · Verizon Far Edge',
    industry_key: 'telecommunications',
    document_class: 'robot_framework_xml',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/robot-framework-v1',
    fields: [
      { name: 'cycle_id',           desc: 'Certification cycle id',          type: 'string', confidence: 99.9, required: true,  validations: [
        { id: 'r1', kind: 'regex', value: '^CYCLE-\\d{8}-CAAS-[A-C]-\\d{4}', error_message: 'Must match CYCLE-YYYYMMDD-CAAS-X-NNNN.' },
      ]},
      { name: 'device_under_test',  desc: 'Device (e.g. CaaS-Node-Type-B)',  type: 'string', confidence: 99.7, required: true,  validations: [] },
      { name: 'firmware_version',   desc: 'Wind River firmware version',     type: 'string', confidence: 99.6, required: true,  validations: [] },
      { name: 'total_tests',        desc: 'Total test count',                type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'passed_tests',       desc: 'Number passed',                   type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'failed_tests',       desc: 'Number failed',                   type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'warn_tests',         desc: 'Number warning (within tolerance)', type: 'number', confidence: 100, required: true,  validations: [] },
      { name: 'test_results',       desc: 'Array of per-test results',       type: 'array',  confidence: 99.2, required: true,  validations: [] },
      { name: 'region',             desc: 'Operations region',               type: 'string', confidence: 97.4, required: false, validations: [] },
      { name: 'operator',           desc: 'Cert engineer / shift',           type: 'string', confidence: 96.8, required: false, validations: [] },
      { name: 'start_time',         desc: 'Cycle start timestamp',           type: 'date',   confidence: 99.1, required: true,  validations: [] },
      { name: 'end_time',           desc: 'Cycle end timestamp',             type: 'date',   confidence: 99.1, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'pass_rate_pct', formula: '(passed_tests / total_tests) * 100', type: 'number' },
      { name: 'gate_passed',   formula: 'pass_rate_pct >= 95',                type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Gate threshold',     detail: 'Cycles below 95% pass rate require HITL approval before wave authorization.', active: true },
      { label: 'Mandatory anchors',  detail: 'cycle_id, device_under_test, firmware_version must all be present.',           active: true },
    ],
  },

  'bp-tel-redfish': {
    id: 'bp-tel-redfish',
    name: 'Redfish Schema Diff Analyzer',
    version: 'v1.0',
    description: 'Compares two Redfish schema snapshots and emits a structured diff (renames, relocations, new-required fields). Tracks every breaking change with a stable id so subsequent runs deduplicate cleanly.',
    industry_label: 'Telecommunications · Verizon Far Edge',
    industry_key: 'telecommunications',
    document_class: 'redfish_schema_diff',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/redfish-schema-v1',
    fields: [
      { name: 'baseline_version',     desc: 'Baseline schema version (e.g. v1.14.0)',  type: 'string', confidence: 99.6, required: true,  validations: [
        { id: 's1', kind: 'regex', value: '^v\\d+\\.\\d+\\.\\d+$', error_message: 'Schema version must be semver vN.N.N.' },
      ]},
      { name: 'current_version',      desc: 'Current schema version (e.g. v1.16.0)',   type: 'string', confidence: 99.6, required: true,  validations: [] },
      { name: 'breaking_changes',     desc: 'Array of breaking changes',                type: 'array',  confidence: 98.4, required: true,  validations: [] },
      { name: 'non_breaking_changes', desc: 'Array of non-breaking additions',         type: 'array',  confidence: 97.2, required: false, validations: [] },
      { name: 'change_type',          desc: 'rename / path_migration / new_required',   type: 'enum',   confidence: 98.9, required: true,  validations: [
        { id: 's2', kind: 'enum_values', value: 'field_rename,path_migration,new_required_field,field_removed,field_added_optional', error_message: 'Unsupported change_type.' },
      ]},
      { name: 'endpoint_path',        desc: 'Redfish endpoint path',                    type: 'string', confidence: 99.7, required: true,  validations: [] },
      { name: 'field_old',            desc: 'Old field name / path',                    type: 'string', confidence: 97.4, required: false, validations: [] },
      { name: 'field_new',            desc: 'New field name / path',                    type: 'string', confidence: 97.4, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'breaking_count',       formula: 'breaking_changes.length',                  type: 'number' },
      { name: 'requires_remediation', formula: 'breaking_changes.length > 0',              type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Auto-epic',     detail: 'Any breaking_count > 0 opens APEXVZ-SCHEMA-EPIC-{cycle} automatically.', active: true },
      { label: 'Wave hold',     detail: 'Any wave that touches an impacted script is held until the epic closes.', active: true },
    ],
  },

  'bp-tel-runbook': {
    id: 'bp-tel-runbook',
    name: 'Upgrade Runbook Extractor',
    version: 'v1.0',
    description: 'Extracts supported upgrade-path steps from VZ-Upgrade-Procedures-2026 (Rev 4). Returns valid + skip + blocked target firmware versions per device type and source firmware.',
    industry_label: 'Telecommunications · Verizon Far Edge',
    industry_key: 'telecommunications',
    document_class: 'upgrade_runbook',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/upgrade-runbook-v1',
    fields: [
      { name: 'device_type',          desc: 'CaaS node device class',          type: 'string', confidence: 99.4, required: true,  validations: [
        { id: 'u1', kind: 'enum_values', value: 'CaaS-Node-Type-A,CaaS-Node-Type-B,CaaS-Node-Type-C', error_message: 'Unsupported device_type.' },
      ]},
      { name: 'source_firmware',      desc: 'Source firmware (e.g. 24.06)',     type: 'string', confidence: 99.6, required: true,  validations: [] },
      { name: 'valid_targets',        desc: 'Valid target firmware versions',   type: 'array',  confidence: 98.2, required: true,  validations: [] },
      { name: 'skip_targets',         desc: 'Targets requiring N+1 step',       type: 'array',  confidence: 95.4, required: false, validations: [] },
      { name: 'blocked_targets',      desc: 'Blocked targets (vendor-rejected)',type: 'array',  confidence: 97.1, required: false, validations: [] },
      { name: 'estimated_duration',   desc: 'Estimated upgrade duration',       type: 'string', confidence: 92.8, required: false, validations: [] },
      { name: 'rollback_supported',   desc: 'Rollback path exists?',            type: 'boolean',confidence: 99.0, required: true,  validations: [] },
      { name: 'pre_check_required',   desc: 'Required pre-upgrade checks',       type: 'array',  confidence: 96.7, required: true,  validations: [] },
      { name: 'post_check_required',  desc: 'Required post-upgrade checks',     type: 'array',  confidence: 96.7, required: true,  validations: [] },
      { name: 'reference_section',    desc: 'Reference doc section anchor',      type: 'string', confidence: 98.9, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'is_supported', formula: 'valid_targets.length > 0', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'No skip-level',  detail: 'Skip-level upgrades fail validation unless explicitly allowed by vendor advisory.', active: true },
    ],
  },

  'bp-tel-kb': {
    id: 'bp-tel-kb',
    name: 'Known Issues KB Article',
    version: 'v1.0',
    description: 'Parses Verizon Known Issues KB articles (KB-2026-*) to surface remediation steps + permanent-fix versions. Used by the schema-drift response and the certification cycle to attach KB references to ticket descriptions.',
    industry_label: 'Telecommunications · Verizon Far Edge',
    industry_key: 'telecommunications',
    document_class: 'known_issues_kb',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/known-issues-v1',
    fields: [
      { name: 'kb_id',                desc: 'KB article id (e.g. KB-2026-0118)', type: 'string', confidence: 100,  required: true,  validations: [
        { id: 'k1', kind: 'regex', value: '^KB-\\d{4}-\\d{4}$', error_message: 'Must match KB-YYYY-NNNN.' },
      ]},
      { name: 'title',                desc: 'KB title',                          type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'severity',             desc: 'Severity classification',           type: 'enum',   confidence: 99.0, required: true,  validations: [
        { id: 'k2', kind: 'enum_values', value: 'critical,high,medium,low,informational', error_message: 'Unsupported severity.' },
      ]},
      { name: 'affected_devices',     desc: 'Devices affected',                   type: 'array',  confidence: 97.6, required: true,  validations: [] },
      { name: 'affected_firmware',    desc: 'Firmware versions affected',         type: 'array',  confidence: 98.1, required: true,  validations: [] },
      { name: 'symptoms',             desc: 'Observable symptoms',                type: 'string', confidence: 96.4, required: true,  validations: [] },
      { name: 'root_cause',           desc: 'Confirmed or hypothesized cause',    type: 'string', confidence: 95.1, required: true,  validations: [] },
      { name: 'workaround',           desc: 'Workaround steps',                   type: 'string', confidence: 96.7, required: true,  validations: [] },
      { name: 'permanent_fix_version', desc: 'Firmware version with permanent fix', type: 'string', confidence: 94.8, required: false, validations: [] },
      { name: 'linked_jira_tickets',  desc: 'Linked JIRA tickets',                type: 'array',  confidence: 92.4, required: false, validations: [] },
      { name: 'related_kb_ids',       desc: 'Cross-referenced KB ids',            type: 'array',  confidence: 91.0, required: false, validations: [] },
    ],
    virtual_fields: [
      { name: 'has_permanent_fix', formula: 'permanent_fix_version IS NOT NULL', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Critical surfacing', detail: 'severity == critical attaches the KB to every ticket on the affected device type.', active: true },
    ],
  },

  'bp-tel-cert-rpt': {
    id: 'bp-tel-cert-rpt',
    name: 'Certification Report Generator',
    version: 'v1.0',
    description: 'Generates the final cycle report (PDF + JSON). Includes executive summary, per-test failure analysis, schema_drift summary, deployment recommendation, and the Audit Lens governance trail.',
    industry_label: 'Telecommunications · Verizon Far Edge',
    industry_key: 'telecommunications',
    document_class: 'certification_report',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/certification-report-v1',
    fields: [
      { name: 'report_id',               desc: 'Certification report id',                 type: 'string', confidence: 100,  required: true,  validations: [] },
      { name: 'cycle_id',                desc: 'Source cycle id',                          type: 'string', confidence: 99.9, required: true,  validations: [] },
      { name: 'overall_status',          desc: 'PASS / FAIL / CONDITIONAL_PASS',           type: 'enum',   confidence: 100,  required: true,  validations: [
        { id: 'c1', kind: 'enum_values', value: 'PASS,FAIL,CONDITIONAL_PASS', error_message: 'overall_status must be PASS/FAIL/CONDITIONAL_PASS.' },
      ]},
      { name: 'deployment_recommendation', desc: 'PROCEED / CONDITIONAL / HOLD',          type: 'enum',   confidence: 99.4, required: true,  validations: [
        { id: 'c2', kind: 'enum_values', value: 'PROCEED,CONDITIONAL,HOLD', error_message: 'Recommendation must be PROCEED/CONDITIONAL/HOLD.' },
      ]},
      { name: 'p1_count',                desc: 'Production-blocker failures',              type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'p2_count',                desc: 'Cycle-blocker failures',                  type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'p3_count',                desc: 'Monitor-level findings',                   type: 'number', confidence: 100,  required: true,  validations: [] },
      { name: 'failure_analysis',        desc: 'Per-test failure detail array',            type: 'array',  confidence: 98.7, required: true,  validations: [] },
      { name: 'schema_drift_summary',    desc: 'Schema drift events surfaced this cycle',  type: 'array',  confidence: 97.8, required: false, validations: [] },
      { name: 'jira_tickets_opened',     desc: 'JIRA tickets opened by this cycle',        type: 'array',  confidence: 99.6, required: true,  validations: [] },
      { name: 'audit_lens_event_ids',    desc: 'Audit Lens event ids linked to this cycle',type: 'array',  confidence: 100,  required: true,  validations: [] },
      { name: 'hours_saved_vs_manual',   desc: 'Hours saved vs. manual cert process',      type: 'number', confidence: 99.0, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'gate_passed', formula: 'p1_count == 0', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'HITL gate',         detail: 'Any P1 > 20 OR schema_drift_summary length > 5 pauses for HITL approval.',  active: true },
      { label: 'Auto-Audit-Lens',   detail: 'Every report generation emits a DVR-{ts}-CERT event, immutably hashed.',     active: true },
    ],
  },
};

// ─────────────────────── Oil & Gas Midstream · EPROD blueprints ───────────────────────
// 6 blueprints mirror the JSON on disk under blueprints/oil_gas_midstream/.
// Last-resort fallback rendered when API is unreachable (apiQuery.isError).

const EPROD_BLUEPRINT_DATA: Record<string, BlueprintData> = {
  'bp-eprod-invoice': {
    id: 'bp-eprod-invoice',
    name: 'EPROD Vendor Invoice',
    version: 'v1.0',
    description: 'Vendor invoice schema covering header, line items, asset code, MSA reference, and tax code for EPROD accounts payable. Halliburton, Schlumberger, Baker Hughes, Kiewit.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'vendor_invoice',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/invoice-v1',
    fields: [
      { name: 'vendor_name',     desc: 'Legal vendor name as printed on the invoice',      type: 'string', confidence: 99.4, required: true,  validations: [
        { id: 'e1', kind: 'min_length', value: '2', error_message: 'Vendor name is too short.' },
      ]},
      { name: 'invoice_number',  desc: 'Unique vendor invoice number',                     type: 'string', confidence: 99.1, required: true,  validations: [
        { id: 'e2', kind: 'min_length', value: '3', error_message: 'Invoice number is too short.' },
      ]},
      { name: 'invoice_date',    desc: 'Date the invoice was issued',                      type: 'date',   confidence: 98.7, required: true,  validations: [] },
      { name: 'po_reference',    desc: 'Referenced EPROD purchase order number (or null)', type: 'string', confidence: 96.2, required: false, validations: [
        { id: 'e3', kind: 'regex', value: '^PO-EPROD-\\d{6,8}$', error_message: 'Must match PO-EPROD-NNNNNN format.' },
      ]},
      { name: 'msa_reference',   desc: 'Referenced master service agreement id',           type: 'string', confidence: 97.8, required: true,  validations: [
        { id: 'e4', kind: 'regex', value: '^MSA-[A-Z]{3,5}-\\d{4}$', error_message: 'Must match MSA-VEN-YYYY.' },
      ]},
      { name: 'asset_code',      desc: 'EPROD asset / cost center (e.g. PIP-12345)',       type: 'string', confidence: 98.4, required: true,  validations: [] },
      { name: 'line_items',      desc: 'Line items with description, qty, unit_price',     type: 'array',  confidence: 95.1, required: true,  validations: [] },
      { name: 'subtotal',        desc: 'Pre-tax subtotal',                                 type: 'number', confidence: 99.4, required: true,  validations: [
        { id: 'e5', kind: 'min', value: '0', error_message: 'Subtotal must be >= 0.' },
      ]},
      { name: 'sales_tax',       desc: 'Sales / use tax amount',                           type: 'number', confidence: 98.4, required: true,  validations: [] },
      { name: 'tax_code',        desc: 'TX-E exempt / TX-I industrial / TX-S sales',       type: 'enum',   confidence: 97.2, required: true,  validations: [
        { id: 'e6', kind: 'enum_values', value: 'TX-E,TX-I,TX-S', error_message: 'tax_code must be TX-E / TX-I / TX-S.' },
      ]},
      { name: 'total',           desc: 'Invoice total amount',                             type: 'number', confidence: 99.6, required: true,  validations: [] },
      { name: 'due_date',        desc: 'Payment due date',                                 type: 'date',   confidence: 97.4, required: true,  validations: [] },
      { name: 'payment_terms',   desc: 'NET30, NET45, etc.',                              type: 'string', confidence: 98.1, required: true,  validations: [] },
      { name: 'currency',        desc: 'ISO currency code (USD default)',                  type: 'string', confidence: 99.7, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'subtotal_plus_tax', formula: 'subtotal + sales_tax', type: 'number' },
      { name: 'is_non_po',         formula: 'po_reference == null',  type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'MSA gate',           detail: 'msa_reference is required for every vendor invoice.', active: true },
      { label: 'HITL threshold',     detail: 'total > $50K AND is_non_po → human review required.', active: true },
      { label: 'Variance flag',      detail: 'Per-line variance vs MSA rate > 2% blocks auto-approval.', active: true },
    ],
  },

  'bp-eprod-po': {
    id: 'bp-eprod-po',
    name: 'EPROD Purchase Order',
    version: 'v1.0',
    description: 'PO schema covering header, line items, MSA reference, asset code, tax code, and approval chain. Pre-pay validation against MSA scope + contracted rates.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'purchase_order',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/purchase-order-v1',
    fields: [
      { name: 'po_number',         desc: 'EPROD PO number',                              type: 'string', confidence: 99.6, required: true,  validations: [
        { id: 'p1', kind: 'regex', value: '^PO-EPROD-\\d{6,8}$', error_message: 'Must match PO-EPROD-NNNNNN.' },
      ]},
      { name: 'vendor_name',       desc: 'Vendor legal name',                            type: 'string', confidence: 99.2, required: true,  validations: [] },
      { name: 'msa_reference',     desc: 'Referenced MSA id',                            type: 'string', confidence: 98.4, required: true,  validations: [] },
      { name: 'asset_code',        desc: 'EPROD asset / cost center code',               type: 'string', confidence: 98.7, required: true,  validations: [] },
      { name: 'po_date',           desc: 'PO issue date',                                type: 'date',   confidence: 99.1, required: true,  validations: [] },
      { name: 'requested_by',      desc: 'Requestor name',                               type: 'string', confidence: 97.4, required: true,  validations: [] },
      { name: 'requested_for',     desc: 'End-user / department',                        type: 'string', confidence: 96.8, required: true,  validations: [] },
      { name: 'ship_to',           desc: 'Ship-to address or facility code',             type: 'string', confidence: 95.7, required: true,  validations: [] },
      { name: 'line_items',        desc: 'Line items with qty, unit_price, msa_scope',   type: 'array',  confidence: 96.8, required: true,  validations: [] },
      { name: 'subtotal',          desc: 'Pre-tax subtotal',                             type: 'number', confidence: 99.4, required: true,  validations: [] },
      { name: 'sales_tax',         desc: 'Tax amount',                                   type: 'number', confidence: 98.4, required: true,  validations: [] },
      { name: 'tax_code',          desc: 'TX-E / TX-I / TX-S',                          type: 'enum',   confidence: 97.1, required: true,  validations: [
        { id: 'p2', kind: 'enum_values', value: 'TX-E,TX-I,TX-S', error_message: 'Tax code must match asset class.' },
      ]},
      { name: 'total',             desc: 'PO total',                                     type: 'number', confidence: 99.7, required: true,  validations: [] },
      { name: 'billing_terms',     desc: 'Billing instructions',                         type: 'string', confidence: 96.4, required: true,  validations: [] },
      { name: 'expected_delivery', desc: 'Expected delivery / completion date',          type: 'date',   confidence: 94.2, required: true,  validations: [] },
      { name: 'approval_chain',    desc: 'Approval entries (approver, role, date)',      type: 'array',  confidence: 95.4, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'requires_director', formula: 'total > 250000',  type: 'boolean' },
      { name: 'po_age_days',       formula: 'today() - po_date', type: 'number' },
    ],
    blueprint_rules: [
      { label: 'MSA scope gate',  detail: 'Every line must map to an MSA Schedule B scope category.', active: true },
      { label: 'Rate variance',   detail: 'Per-line rate variance vs MSA > 5% blocks auto-approval.',  active: true },
      { label: 'Director review', detail: 'PO total > $250K routes to director regardless of compliance.', active: true },
    ],
  },

  'bp-eprod-msa': {
    id: 'bp-eprod-msa',
    name: 'EPROD Master Service Agreement',
    version: 'v1.0',
    description: 'MSA schema covering identity, term, scope categories, rate card, billing terms, indemnity clauses, and approval thresholds.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'master_service_agreement',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/msa-v1',
    fields: [
      { name: 'msa_id',              desc: 'MSA identifier (e.g. MSA-HAL-2024)',         type: 'string', confidence: 99.8, required: true,  validations: [
        { id: 'm1', kind: 'regex', value: '^MSA-[A-Z]{3,5}-\\d{4}$', error_message: 'Must match MSA-VEN-YYYY.' },
      ]},
      { name: 'vendor_name',         desc: 'Vendor legal name',                          type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'msa_type',            desc: 'services / equipment / EPC',                 type: 'enum',   confidence: 98.1, required: true,  validations: [
        { id: 'm2', kind: 'enum_values', value: 'services,equipment,EPC,construction', error_message: 'Unsupported MSA type.' },
      ]},
      { name: 'effective_date',      desc: 'MSA effective date',                         type: 'date',   confidence: 98.6, required: true,  validations: [] },
      { name: 'expiration_date',     desc: 'MSA expiration date',                        type: 'date',   confidence: 98.4, required: true,  validations: [] },
      { name: 'scope_categories',    desc: 'Schedule B scope categories',                 type: 'array',  confidence: 96.7, required: true,  validations: [] },
      { name: 'rate_card',           desc: 'Rate card entries (asset, unit, rate)',       type: 'array',  confidence: 95.8, required: true,  validations: [] },
      { name: 'billing_terms',       desc: 'Billing cycle + submission requirements',     type: 'string', confidence: 96.2, required: true,  validations: [] },
      { name: 'payment_terms',       desc: 'Net payment terms',                          type: 'string', confidence: 98.1, required: true,  validations: [] },
      { name: 'indemnity_clauses',   desc: 'Indemnity / liability clauses + refs',        type: 'array',  confidence: 92.4, required: false, validations: [] },
      { name: 'approval_thresholds', desc: 'DOA thresholds by role',                      type: 'array',  confidence: 97.1, required: true,  validations: [] },
      { name: 'governing_law',       desc: 'Governing law jurisdiction',                  type: 'string', confidence: 98.7, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'is_active',     formula: 'today() >= effective_date AND today() < expiration_date', type: 'boolean' },
      { name: 'months_to_exp', formula: 'months_between(today(), expiration_date)',                  type: 'number'  },
    ],
    blueprint_rules: [
      { label: 'Active window',    detail: 'Only MSAs where today is between effective_date and expiration_date are usable.', active: true },
      { label: 'Renewal alert',    detail: 'months_to_exp < 3 triggers procurement renewal workflow.', active: true },
    ],
  },

  'bp-eprod-quote': {
    id: 'bp-eprod-quote',
    name: 'EPROD Engineering Quote',
    version: 'v1.0',
    description: 'Engineering quote schema covering vendor, scope, milestone pricing, total estimate, validity, terms, and exclusions. Fluor / Bechtel / Emerson intake.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'engineering_quote',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/engineering-quote-v1',
    fields: [
      { name: 'quote_number',       desc: 'Vendor quote / proposal number',          type: 'string', confidence: 99.1, required: true,  validations: [] },
      { name: 'vendor_name',        desc: 'EPC vendor name',                          type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'project_name',       desc: 'EPROD project name or code',               type: 'string', confidence: 97.6, required: true,  validations: [] },
      { name: 'scope_description',  desc: 'Free-text scope summary',                  type: 'string', confidence: 92.8, required: true,  validations: [] },
      { name: 'milestones',         desc: 'Milestones (name, duration_days, price)',  type: 'array',  confidence: 93.2, required: true,  validations: [] },
      { name: 'unit_pricing',       desc: 'Unit pricing for time + materials',        type: 'array',  confidence: 91.7, required: true,  validations: [] },
      { name: 'total_estimate',     desc: 'Quoted total estimate',                    type: 'number', confidence: 99.4, required: true,  validations: [
        { id: 'q1', kind: 'min', value: '0', error_message: 'Total must be >= 0.' },
      ]},
      { name: 'validity_until',     desc: 'Quote validity expiration',                type: 'date',   confidence: 96.8, required: true,  validations: [] },
      { name: 'terms',              desc: 'Payment + execution terms',                type: 'string', confidence: 92.4, required: true,  validations: [] },
      { name: 'optional_services',  desc: 'Optional services priced separately',      type: 'array',  confidence: 88.7, required: false, validations: [] },
      { name: 'references',         desc: 'References / past-performance citations',  type: 'array',  confidence: 87.4, required: false, validations: [] },
      { name: 'rfp_reference',      desc: 'Linked RFP / RFQ number if any',           type: 'string', confidence: 91.2, required: false, validations: [] },
      { name: 'exclusions',         desc: 'Explicit scope exclusions',                type: 'array',  confidence: 89.7, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'days_to_expiry', formula: 'validity_until - today()', type: 'number' },
    ],
    blueprint_rules: [
      { label: 'Validity gate',  detail: 'days_to_expiry > 14 required for procurement review.', active: true },
      { label: 'Historical compare', detail: 'Compare total_estimate vs 12-month median for same scope_category.', active: true },
    ],
  },

  'bp-eprod-tariff': {
    id: 'bp-eprod-tariff',
    name: 'EPROD FERC Tariff Sheet',
    version: 'v1.0',
    description: 'WOW · FERC tariff schema covering docket, pipeline, commodity, effective window, zones, rate schedules, commodity + reservation charges, fuel retention, surcharges, and PPI-FG indexing.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'ferc_tariff',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/ferc-tariff-v1',
    fields: [
      { name: 'tariff_id',           desc: 'Tariff sheet identifier',                   type: 'string', confidence: 99.8, required: true,  validations: [] },
      { name: 'ferc_docket',         desc: 'FERC docket number (RP / IS series)',        type: 'string', confidence: 99.4, required: true,  validations: [
        { id: 't1', kind: 'regex', value: '^(RP|IS)\\d{2}-\\d{3,5}-\\d{3}$', error_message: 'Must match FERC docket format.' },
      ]},
      { name: 'pipeline_name',       desc: 'Pipeline operator + system name',            type: 'string', confidence: 99.6, required: true,  validations: [] },
      { name: 'commodity',           desc: 'natural gas / crude / NGL / refined',        type: 'enum',   confidence: 99.2, required: true,  validations: [
        { id: 't2', kind: 'enum_values', value: 'natural_gas,crude,NGL,refined_products', error_message: 'Unsupported commodity.' },
      ]},
      { name: 'effective_date',      desc: 'Tariff effective date (gas-day start)',      type: 'date',   confidence: 99.2, required: true,  validations: [] },
      { name: 'expiration_date',     desc: 'Tariff expiration / supersession date',      type: 'date',   confidence: 96.8, required: false, validations: [] },
      { name: 'zones',               desc: 'Zone defs (id, receipt/delivery points)',    type: 'array',  confidence: 97.4, required: true,  validations: [] },
      { name: 'rate_schedules',      desc: 'Rate schedules (id, description, scope)',    type: 'array',  confidence: 96.8, required: true,  validations: [] },
      { name: 'commodity_charges',   desc: 'Commodity charge rows ($/unit) per zone',    type: 'array',  confidence: 96.2, required: true,  validations: [] },
      { name: 'reservation_charges', desc: 'Reservation charge rows ($/unit) per zone',  type: 'array',  confidence: 96.4, required: true,  validations: [] },
      { name: 'fuel_retention_pct',  desc: 'Fuel retention percentage',                  type: 'number', confidence: 94.7, required: false, validations: [
        { id: 't3', kind: 'min', value: '0',  error_message: 'Fuel retention >= 0.' },
        { id: 't4', kind: 'max', value: '20', error_message: 'Fuel retention > 20% is implausible.' },
      ]},
      { name: 'surcharges',          desc: 'Authorized surcharges (ACA, GHG, etc.)',     type: 'array',  confidence: 92.4, required: false, validations: [] },
      { name: 'ppi_fg_index_link',   desc: 'BLS PPI-FG series id for indexed adjustment', type: 'string', confidence: 89.7, required: false, validations: [] },
      { name: 'applicable_shippers', desc: 'Shipper classes the tariff applies to',      type: 'array',  confidence: 95.7, required: true,  validations: [] },
      { name: 'filing_metadata',     desc: 'filed_by, accepted_date, supersedes_tariff_id', type: 'object', confidence: 96.4, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'is_currently_effective', formula: 'today() >= effective_date AND (expiration_date == null OR today() < expiration_date)', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'Variance threshold', detail: 'Shipper-invoice rate > 1.5% above effective tariff = overbilling flag.', active: true },
      { label: 'July 1 indexing',    detail: 'PPI-FG annual indexed adjustment applied effective gas-day Jul 1.',    active: true },
      { label: 'Monthly aggregation', detail: 'Cumulative monthly exposure > $250K triggers director escalation.',     active: true },
    ],
  },

  'bp-eprod-jib': {
    id: 'bp-eprod-jib',
    name: 'EPROD JIB Statement',
    version: 'v1.0',
    description: 'WOW · Joint Interest Billing schema covering JV, operator, AFE references, working-interest math, capital + operating charges, partner share, prior-period adjustments, and cumulative position.',
    industry_label: 'Oil & Gas Midstream · EPROD',
    industry_key: 'oil_gas_midstream',
    document_class: 'jib_statement',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/jib-statement-v1',
    fields: [
      { name: 'statement_id',             desc: 'JIB statement identifier',                  type: 'string', confidence: 99.8, required: true,  validations: [] },
      { name: 'jv_name',                  desc: 'JV name (e.g. Sweeny Frac, Mont Belvieu)',  type: 'string', confidence: 99.4, required: true,  validations: [] },
      { name: 'operator',                 desc: 'Operating partner (Phillips 66, Targa)',     type: 'string', confidence: 99.2, required: true,  validations: [] },
      { name: 'afe_reference',            desc: 'AFE / project reference id',                 type: 'string', confidence: 98.7, required: true,  validations: [
        { id: 'j1', kind: 'regex', value: '^AFE-\\d{4}-\\d{3,4}$', error_message: 'Must match AFE-YYYY-NNN.' },
      ]},
      { name: 'billing_period',           desc: 'Statement billing period (YYYY-MM)',         type: 'string', confidence: 99.4, required: true,  validations: [
        { id: 'j2', kind: 'regex', value: '^\\d{4}-\\d{2}$', error_message: 'Must match YYYY-MM.' },
      ]},
      { name: 'working_interest_pct',     desc: 'EPROD working interest per JOA',             type: 'number', confidence: 99.1, required: true,  validations: [
        { id: 'j3', kind: 'min', value: '0',   error_message: 'WI must be >= 0.' },
        { id: 'j4', kind: 'max', value: '100', error_message: 'WI must be <= 100.' },
      ]},
      { name: 'capital_charges',          desc: 'Capital line items (desc, gross_usd, afe)',  type: 'array',  confidence: 96.8, required: true,  validations: [] },
      { name: 'operating_charges',        desc: 'Operating line items (desc, gross_usd, afe)', type: 'array',  confidence: 96.4, required: true,  validations: [] },
      { name: 'gross_total',              desc: 'Total gross charges for the period',         type: 'number', confidence: 99.4, required: true,  validations: [] },
      { name: 'partner_share',            desc: 'EPROD partner share = gross * wi_pct',       type: 'number', confidence: 99.2, required: true,  validations: [] },
      { name: 'prior_period_adjustments', desc: 'Prior-period adjustments + original cycle',  type: 'array',  confidence: 92.4, required: false, validations: [] },
      { name: 'cumulative_to_date',       desc: 'Cumulative AFE charges through statement',   type: 'number', confidence: 98.4, required: true,  validations: [] },
      { name: 'supporting_invoices',      desc: 'Supporting vendor invoice references',       type: 'array',  confidence: 88.7, required: false, validations: [] },
      { name: 'dispute_period_deadline',  desc: 'Last date to file dispute',                  type: 'date',   confidence: 95.4, required: true,  validations: [] },
    ],
    virtual_fields: [
      { name: 'computed_partner_share', formula: 'gross_total * (working_interest_pct / 100)', type: 'number' },
      { name: 'share_match',             formula: 'abs(partner_share - computed_partner_share) / partner_share <= 0.001', type: 'boolean' },
    ],
    blueprint_rules: [
      { label: 'AFE bounds enforcement', detail: 'cumulative_to_date must remain <= AFE ceiling per JOA.', active: true },
      { label: 'Working-interest math',  detail: 'Reported partner_share must match gross_total * wi_pct within 0.1%.', active: true },
      { label: 'Overrun escalation',     detail: 'Cumulative breach > 5% of AFE escalates to JV Accounting before payment.', active: true },
    ],
  },
};

// ─────────────────────── Safe fallback for unknown ids ───────────────────────
// Per the CLAUDE.md ZERO-HARDCODING RULE: never silently render invoice content
// for an unknown id. Show a clear "not found" stub instead.

const DEFAULT_BLUEPRINT: BlueprintData = {
  id: 'bp-unknown',
  name: 'Blueprint not found',
  version: '—',
  description: 'No blueprint matches this id, and the platform API is unreachable. Verify the id in the URL, or seed the blueprint into DynamoDB via POST /api/v1/blueprints/seed?industry=<industry>.',
  industry_label: '',
  industry_key: '',
  document_class: '',
  status_label: 'Unknown',
  status_chip: 'chip-gray',
  arn: '',
  fields: [],
  virtual_fields: [],
  blueprint_rules: [],
};
