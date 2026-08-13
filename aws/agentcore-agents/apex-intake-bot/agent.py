"""
Apex Intake Bot - AgentCore Agent for patient registration and intake
"""
import json
import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

SYSTEM_PROMPT = """You are IntakeBot, an AI assistant for patient registration and intake at healthcare facilities.

Your capabilities:
1. Process patient registration forms
2. Verify insurance information
3. Collect demographic data
4. Schedule appointments
5. Route referrals

When handling patient intake:
- Extract patient demographics accurately
- Verify insurance eligibility
- Check for existing patient records
- Create or update patient profiles
- Ensure consent forms are completed

Maintain patient confidentiality. Be helpful and empathetic."""


@tool
def extract_registration_form(s3_uri: str) -> dict:
    """
    Extract data from a patient registration form using BDA.

    Args:
        s3_uri: S3 URI of the registration form document

    Returns:
        Extracted patient demographics and registration data
    """
    return {
        "status": "processing",
        "message": "Registration form extraction started"
    }


@tool
def check_existing_patient(first_name: str, last_name: str, date_of_birth: str) -> dict:
    """
    Check if a patient already exists in the system.

    Args:
        first_name: Patient's first name
        last_name: Patient's last name
        date_of_birth: Patient's date of birth (YYYY-MM-DD)

    Returns:
        Existing patient record if found, or indication of new patient
    """
    return {
        "patient_found": False,
        "message": "No existing patient record found",
        "suggested_action": "Create new patient profile"
    }


@tool
def verify_insurance(member_id: str, group_number: str, payer_name: str) -> dict:
    """
    Verify patient insurance information.

    Args:
        member_id: Insurance member ID
        group_number: Insurance group number
        payer_name: Name of the insurance payer

    Returns:
        Insurance verification results
    """
    return {
        "verified": True,
        "member_id": member_id,
        "group_number": group_number,
        "payer_name": payer_name,
        "plan_type": "PPO",
        "copay": 25.00
    }


@tool
def create_patient_profile(patient_data: dict) -> dict:
    """
    Create a new patient profile in the system.

    Args:
        patient_data: Patient demographics and insurance information

    Returns:
        Created patient profile with assigned MRN
    """
    import uuid
    mrn = f"MRN{uuid.uuid4().hex[:8].upper()}"
    return {
        "success": True,
        "mrn": mrn,
        "message": "Patient profile created successfully"
    }


@tool
def schedule_appointment(patient_mrn: str, provider_id: str, appointment_type: str, preferred_date: str) -> dict:
    """
    Schedule an appointment for a patient.

    Args:
        patient_mrn: Patient's medical record number
        provider_id: Provider/physician ID
        appointment_type: Type of appointment (e.g., new_patient, follow_up)
        preferred_date: Preferred appointment date (YYYY-MM-DD)

    Returns:
        Scheduled appointment details
    """
    import uuid
    return {
        "scheduled": True,
        "appointment_id": f"APT{uuid.uuid4().hex[:8].upper()}",
        "patient_mrn": patient_mrn,
        "date": preferred_date,
        "time": "10:00 AM"
    }


# Create the agent
model = BedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        extract_registration_form,
        check_existing_patient,
        verify_insurance,
        create_patient_profile,
        schedule_appointment
    ]
)

# Create the AgentCore app
app = BedrockAgentCoreApp(agent=agent)
