"""
EHR Format - Small Factory
Formats extracted clinical data for EHR system integration.
"""

from typing import Dict, Any, List
from datetime import datetime
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# EHR system templates
EHR_SYSTEMS = {
    "epic": "Epic",
    "cerner": "Cerner",
    "allscripts": "Allscripts",
    "meditech": "Meditech",
    "athena": "AthenaHealth",
    "fhir": "FHIR R4",
}


def format_for_fhir(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format data as FHIR R4 resources."""
    patient = data.get('patient', {})
    clinical = data.get('clinical', {})
    codes = data.get('codes', {})

    resources = []

    # Patient resource
    if patient.get('name'):
        name_info = patient['name']
        patient_resource = {
            "resourceType": "Patient",
            "id": patient.get('mrn', ''),
            "name": [{
                "use": "official",
                "family": name_info.get('last_name', ''),
                "given": [name_info.get('first_name', '')],
            }],
            "birthDate": patient.get('date_of_birth', ''),
        }

        if patient.get('insurance'):
            patient_resource["extension"] = [{
                "url": "http://hl7.org/fhir/StructureDefinition/patient-insurance",
                "valueString": patient['insurance'].get('name', ''),
            }]

        resources.append(patient_resource)

    # Encounter resource
    encounter_resource = {
        "resourceType": "Encounter",
        "id": f"enc-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory",
        },
        "subject": {"reference": f"Patient/{patient.get('mrn', '')}"},
        "period": {
            "start": datetime.now().isoformat(),
        },
    }
    resources.append(encounter_resource)

    # Condition resources (diagnoses)
    for i, icd in enumerate(codes.get('icd_codes', [])):
        if icd.get('code'):
            condition_resource = {
                "resourceType": "Condition",
                "id": f"cond-{i+1}",
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                    }]
                },
                "code": {
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": icd['code'],
                        "display": icd.get('description', icd.get('diagnosis', '')),
                    }]
                },
                "subject": {"reference": f"Patient/{patient.get('mrn', '')}"},
            }
            resources.append(condition_resource)

    # MedicationStatement resources
    for i, med in enumerate(clinical.get('medications', [])):
        med_resource = {
            "resourceType": "MedicationStatement",
            "id": f"med-{i+1}",
            "status": "active",
            "medicationCodeableConcept": {
                "text": med.get('name', ''),
            },
            "subject": {"reference": f"Patient/{patient.get('mrn', '')}"},
            "dosage": [{
                "text": f"{med.get('dose', '')} {med.get('unit', '')} {med.get('frequency', '')}",
            }],
        }
        resources.append(med_resource)

    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [{"resource": r} for r in resources],
    }


def format_for_hl7v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format data as HL7 v2.x message segments."""
    patient = data.get('patient', {})
    clinical = data.get('clinical', {})
    codes = data.get('codes', {})

    now = datetime.now()
    segments = []

    # MSH - Message Header
    segments.append({
        "segment": "MSH",
        "fields": {
            "field_separator": "|",
            "encoding_characters": "^~\\&",
            "sending_application": "APEX",
            "message_type": "MDM^T02",
            "message_control_id": f"MSG{now.strftime('%Y%m%d%H%M%S')}",
            "processing_id": "P",
            "version_id": "2.5.1",
        }
    })

    # PID - Patient Identification
    name_info = patient.get('name', {})
    segments.append({
        "segment": "PID",
        "fields": {
            "patient_id": patient.get('mrn', ''),
            "patient_name": f"{name_info.get('last_name', '')}^{name_info.get('first_name', '')}",
            "date_of_birth": patient.get('date_of_birth', ''),
        }
    })

    # DG1 - Diagnosis segments
    for i, icd in enumerate(codes.get('icd_codes', [])):
        if icd.get('code'):
            segments.append({
                "segment": "DG1",
                "fields": {
                    "set_id": i + 1,
                    "diagnosis_coding_method": "ICD-10",
                    "diagnosis_code": icd['code'],
                    "diagnosis_description": icd.get('description', ''),
                }
            })

    return {
        "format": "HL7v2",
        "version": "2.5.1",
        "segments": segments,
    }


def format_for_ccd(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format data as C-CDA (Consolidated Clinical Document Architecture)."""
    patient = data.get('patient', {})
    clinical = data.get('clinical', {})

    return {
        "format": "C-CDA",
        "version": "2.1",
        "document": {
            "typeId": {"root": "2.16.840.1.113883.1.3", "extension": "POCD_HD000040"},
            "templateId": {"root": "2.16.840.1.113883.10.20.22.1.2"},
            "code": {"code": "34133-9", "codeSystem": "2.16.840.1.113883.6.1", "displayName": "Summarization of Episode Note"},
            "title": "Clinical Summary",
            "effectiveTime": datetime.now().isoformat(),
            "recordTarget": {
                "patientRole": {
                    "id": patient.get('mrn', ''),
                    "patient": {
                        "name": patient.get('name', {}),
                        "birthTime": patient.get('date_of_birth', ''),
                    }
                }
            },
            "sections": clinical.get('sections', {}),
        }
    }


@register_factory("ehr_format")
async def ehr_format(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format clinical data for EHR system integration.

    Input:
        patient_identify: Patient information
        clinical_extract: Clinical data
        code_suggest: Coding information
        quality_audit: Quality audit results
        config.ehr_system: Target EHR system
        config.output_format: fhir, hl7v2, ccd

    Output:
        formatted_data: EHR-ready data payload
        format: Output format used
        validation: Validation results
        ready_to_import: Whether data is ready for import
    """
    config = input_data.get('config', {})
    patient = input_data.get('patient_identify', {})
    clinical = input_data.get('clinical_extract', {})
    codes = input_data.get('code_suggest', {})
    quality = input_data.get('quality_audit', {})

    ehr_system = config.get('ehr_system', 'fhir')
    output_format = config.get('output_format', 'fhir')

    # Consolidate data
    consolidated_data = {
        "patient": {
            "mrn": patient.get('mrn'),
            "name": patient.get('patient', {}).get('name'),
            "date_of_birth": patient.get('patient', {}).get('date_of_birth'),
            "insurance": patient.get('patient', {}).get('insurance'),
        },
        "clinical": {
            "sections": clinical.get('sections', {}),
            "vitals": clinical.get('vitals', {}),
            "medications": clinical.get('medications', []),
            "diagnoses": clinical.get('diagnoses', []),
        },
        "codes": {
            "icd_codes": codes.get('icd_codes', []),
            "cpt_codes": codes.get('cpt_codes', []),
        },
    }

    # Format based on target system
    formatters = {
        "fhir": format_for_fhir,
        "hl7v2": format_for_hl7v2,
        "ccd": format_for_ccd,
    }

    formatter = formatters.get(output_format.lower(), format_for_fhir)
    formatted_data = formatter(consolidated_data)

    # Validate output
    validation_errors = []

    if not patient.get('mrn'):
        validation_errors.append("Missing MRN - required for EHR import")
    if not codes.get('icd_codes'):
        validation_errors.append("No ICD codes - may fail billing validation")
    if not quality.get('passed', False):
        validation_errors.append("Quality audit not passed - review documentation")

    # Determine readiness
    ready_to_import = (
        len(validation_errors) == 0 and
        patient.get('verified', False) or patient.get('mrn') is not None
    )

    return {
        "formatted_data": formatted_data,
        "format": output_format,
        "ehr_system": EHR_SYSTEMS.get(ehr_system.lower(), ehr_system),
        "validation_errors": validation_errors,
        "validation_passed": len(validation_errors) == 0,
        "ready_to_import": ready_to_import,
        "patient_mrn": patient.get('mrn'),
        "diagnosis_count": len(codes.get('icd_codes', [])),
        "procedure_count": len(codes.get('cpt_codes', [])),
        "generated_at": datetime.now().isoformat(),
    }
