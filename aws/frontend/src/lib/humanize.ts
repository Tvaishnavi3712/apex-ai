/**
 * humanize — convert backend snake_case identifiers into Title Case display
 * names. Used wherever a raw DynamoDB name (e.g. `policy_procedure_lookup`,
 * `hr_policy_doc`, `work_order_record`) needs to be shown to a human.
 *
 * Special-cases common acronyms (HR, ESW, EDG, MOV, HX, PM, PDF, RCS, ...)
 * so they stay uppercase instead of getting lowercased to "Hr", "Esw", etc.
 *
 * Rules:
 *   1. Replace `_` and `-` with spaces
 *   2. Trim and collapse repeated spaces
 *   3. For each word:
 *      • If it matches a known acronym → uppercase
 *      • Otherwise → first letter upper, rest lower
 *
 * Example:
 *   humanizeName('policy_procedure_lookup')   → 'Policy Procedure Lookup'
 *   humanizeName('hr_policy_doc')             → 'HR Policy Doc'
 *   humanizeName('work-order-record')         → 'Work Order Record'
 *   humanizeName('STP-415_business_travel')   → 'STP-415 Business Travel'
 */

const ACRONYMS = new Set<string>([
  'HR', 'AI', 'ML', 'API', 'AWS', 'PDF', 'PM', 'QC', 'CNC', 'ITAR',
  'STP', 'NRC', 'RCS', 'RHR', 'ESW', 'CCW', 'MFW', 'AFW', 'EDG', 'CVCS',
  'RWST', 'SI', 'CTMT', 'MS', 'CD', 'SW', 'INST', 'FP', 'HVC', 'RAD',
  'SDC', 'CHEM', 'PCC', 'EDS', 'BAT', 'UPS', 'FH',
  'BOM', 'PO', 'WO', 'ETL', 'KPI', 'ROI', 'CRM', 'ERP', 'SAP',
  'BDA', 'SDK', 'SQL', 'JSON', 'YAML', 'XML', 'CSV', 'CIP', 'NERC',
  'IEEE', 'ANSI', 'ASME', 'OSHA', 'ID', 'PTO', 'IRS', 'GSA',
  'MOV', 'HX', 'EDG', 'OPS', 'IT', 'IO', 'OT',
]);

/** Convert one word, honoring acronym list (case-insensitive lookup). */
function _word(w: string): string {
  if (!w) return w;
  // Preserve numeric / alphanumeric-with-dash tokens like "STP-415", "AB-23"
  if (/-/.test(w)) {
    return w.split('-').map(_word).join('-');
  }
  if (ACRONYMS.has(w.toUpperCase())) return w.toUpperCase();
  return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
}

/**
 * Convert a snake_case / kebab-case / mixed identifier to a human-readable
 * Title Case string with acronym handling.
 *
 * Returns the input unchanged when it's empty / not a string.
 */
export function humanizeName(input: string | undefined | null): string {
  if (!input || typeof input !== 'string') return '';
  return input
    .replace(/[_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .map(_word)
    .join(' ');
}
