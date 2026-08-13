"""
S3 Document Connector for SolidWorks PDM and SharePoint GCC High Replacement
Handles CAD drawings, work instructions, and ITAR documents.
"""
import boto3
from datetime import datetime
from typing import Optional, List, Dict, Any
from actions.sdk.action_decorator import apex_action, register_factory


# Configuration
REGION = "us-east-1"
BUCKETS = {
    "cad_vault": "apex-demo-cad-vault",
    "sharepoint": "apex-demo-sharepoint-docs"
}


class S3DocumentConnector:
    """Connector for document retrieval from S3."""

    def __init__(self, region: str = REGION):
        self.s3 = boto3.client('s3', region_name=region)

    def get_object(self, bucket: str, key: str) -> Dict[str, Any]:
        """Get object from S3."""
        try:
            response = self.s3.get_object(Bucket=bucket, Key=key)
            return {
                "body": response['Body'].read(),
                "content_type": response.get('ContentType'),
                "last_modified": response.get('LastModified').isoformat() if response.get('LastModified') else None,
                "size": response.get('ContentLength')
            }
        except self.s3.exceptions.NoSuchKey:
            return {"error": f"Object not found: {key}"}

    def list_objects(self, bucket: str, prefix: str) -> List[Dict[str, Any]]:
        """List objects with prefix."""
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        objects = []
        for obj in response.get('Contents', []):
            objects.append({
                "key": obj['Key'],
                "size": obj['Size'],
                "last_modified": obj['LastModified'].isoformat()
            })

        return objects

    def generate_presigned_url(self, bucket: str, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for secure document access."""
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return url


# ============================================
# SolidWorks PDM Connector (CAD Documents)
# ============================================

@register_factory("pdm_connector")
@apex_action(
    name="get_drawing",
    description="Retrieve drawing by part number and revision",
    industry="aerospace_defense"
)
def get_drawing(part_number: str, revision: str = "latest") -> Dict[str, Any]:
    """
    Retrieve drawing PDF by part number and revision.

    Args:
        part_number: Part number
        revision: Revision letter (A, B, C, etc.) or "latest"

    Returns:
        Drawing document info with presigned URL
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["cad_vault"]

    try:
        if revision.lower() == "latest":
            # List all revisions and get latest
            prefix = f"drawings/{part_number}/"
            objects = connector.list_objects(bucket, prefix)

            if not objects:
                return {"error": f"No drawings found for {part_number}"}

            # Sort by key to get latest revision (assumes Rev_X naming)
            objects.sort(key=lambda x: x['key'], reverse=True)
            key = objects[0]['key']
        else:
            key = f"drawings/{part_number}/{part_number}_Rev_{revision}.pdf"

        # Generate presigned URL for secure access
        url = connector.generate_presigned_url(bucket, key)

        return {
            "part_number": part_number,
            "revision": revision,
            "s3_key": key,
            "download_url": url,
            "url_expires_in": "1 hour",
            "source": "SolidWorks PDM (S3)",
            "connector_mode": "READ",
            "itar_notice": "ITAR controlled - US Persons only"
        }
    except Exception as e:
        return {"error": str(e), "source": "SolidWorks PDM (S3)"}


@register_factory("pdm_connector")
@apex_action(
    name="list_revisions",
    description="List all revisions for a part number",
    industry="aerospace_defense"
)
def list_revisions(part_number: str) -> Dict[str, Any]:
    """
    List all revisions available for a part number.

    Args:
        part_number: Part number to search

    Returns:
        List of available revisions
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["cad_vault"]

    try:
        prefix = f"drawings/{part_number}/"
        objects = connector.list_objects(bucket, prefix)

        revisions = []
        for obj in objects:
            # Extract revision from filename
            filename = obj['key'].split('/')[-1]
            if '_Rev_' in filename:
                rev = filename.split('_Rev_')[1].split('.')[0]
                revisions.append({
                    "revision": rev,
                    "filename": filename,
                    "size_kb": round(obj['size'] / 1024, 1),
                    "last_modified": obj['last_modified']
                })

        revisions.sort(key=lambda x: x['revision'], reverse=True)

        return {
            "part_number": part_number,
            "revisions": revisions,
            "total_revisions": len(revisions),
            "latest_revision": revisions[0]['revision'] if revisions else None,
            "source": "SolidWorks PDM (S3)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "SolidWorks PDM (S3)"}


@register_factory("pdm_connector")
@apex_action(
    name="get_gcode_program",
    description="Retrieve CNC program from repository",
    industry="aerospace_defense"
)
def get_gcode_program(program_name: str) -> Dict[str, Any]:
    """
    Retrieve CNC G-code program from repository.

    Args:
        program_name: Program filename (e.g., TG-5842-001_Mazak_Rough.nc)

    Returns:
        G-code content
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["cad_vault"]

    try:
        key = f"programs/{program_name}"
        result = connector.get_object(bucket, key)

        if "error" in result:
            return result

        return {
            "program_name": program_name,
            "content": result['body'].decode('utf-8'),
            "size_bytes": result['size'],
            "last_modified": result['last_modified'],
            "source": "CNC Program Repository (S3)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "CNC Program Repository (S3)"}


@register_factory("pdm_connector")
@apex_action(
    name="list_gcode_programs",
    description="List available CNC programs",
    industry="aerospace_defense"
)
def list_gcode_programs(part_number: Optional[str] = None) -> Dict[str, Any]:
    """
    List available CNC programs, optionally filtered by part number.

    Args:
        part_number: Optional part number filter

    Returns:
        List of available programs
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["cad_vault"]

    try:
        prefix = "programs/"
        objects = connector.list_objects(bucket, prefix)

        programs = []
        for obj in objects:
            filename = obj['key'].split('/')[-1]
            if filename.endswith('.nc'):
                if part_number is None or part_number in filename:
                    programs.append({
                        "program_name": filename,
                        "size_kb": round(obj['size'] / 1024, 1),
                        "last_modified": obj['last_modified']
                    })

        return {
            "programs": programs,
            "total_programs": len(programs),
            "filter_applied": part_number,
            "source": "CNC Program Repository (S3)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "CNC Program Repository (S3)"}


# ============================================
# SharePoint GCC High Connector (Documents)
# ============================================

@register_factory("sharepoint_connector")
@apex_action(
    name="get_work_instruction",
    description="Get work instruction document",
    industry="aerospace_defense"
)
def get_work_instruction(wi_number: str, revision: str = "latest") -> Dict[str, Any]:
    """
    Get work instruction document by WI number.

    Args:
        wi_number: Work instruction number (e.g., WI-MILL-001)
        revision: Revision letter or "latest"

    Returns:
        Work instruction document info with presigned URL
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["sharepoint"]

    try:
        if revision.lower() == "latest":
            prefix = f"work-instructions/{wi_number}"
            objects = connector.list_objects(bucket, prefix)

            if not objects:
                return {"error": f"No work instruction found for {wi_number}"}

            objects.sort(key=lambda x: x['key'], reverse=True)
            key = objects[0]['key']
        else:
            key = f"work-instructions/{wi_number}_Rev_{revision}.pdf"

        url = connector.generate_presigned_url(bucket, key)

        return {
            "wi_number": wi_number,
            "revision": revision,
            "s3_key": key,
            "download_url": url,
            "url_expires_in": "1 hour",
            "source": "SharePoint GCC High (S3)",
            "connector_mode": "READ",
            "classification": "CUI"
        }
    except Exception as e:
        return {"error": str(e), "source": "SharePoint GCC High (S3)"}


@register_factory("sharepoint_connector")
@apex_action(
    name="get_rfp_document",
    description="Get RFP or proposal document",
    industry="aerospace_defense"
)
def get_rfp_document(document_name: str) -> Dict[str, Any]:
    """
    Get RFP or proposal document.

    Args:
        document_name: Document filename

    Returns:
        Document content
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["sharepoint"]

    try:
        key = f"rfp/{document_name}"
        result = connector.get_object(bucket, key)

        if "error" in result:
            return result

        content = result['body'].decode('utf-8')

        return {
            "document_name": document_name,
            "content": content,
            "size_bytes": result['size'],
            "last_modified": result['last_modified'],
            "source": "SharePoint GCC High (S3)",
            "connector_mode": "READ",
            "classification": "CUI // ITAR Controlled"
        }
    except Exception as e:
        return {"error": str(e), "source": "SharePoint GCC High (S3)"}


@register_factory("sharepoint_connector")
@apex_action(
    name="list_program_documents",
    description="List all documents for a program",
    industry="aerospace_defense"
)
def list_program_documents(program: str) -> Dict[str, Any]:
    """
    List all documents for a specific program.

    Args:
        program: Program name (F-35, F-22, UH-60, C-17)

    Returns:
        List of program documents
    """
    connector = S3DocumentConnector()
    bucket = BUCKETS["sharepoint"]

    try:
        # Search across multiple prefixes
        documents = []
        prefixes = ["rfp/", "work-instructions/", "quality/"]

        for prefix in prefixes:
            objects = connector.list_objects(bucket, prefix)
            for obj in objects:
                filename = obj['key'].split('/')[-1]
                if program.upper() in filename.upper():
                    documents.append({
                        "filename": filename,
                        "category": prefix.rstrip('/'),
                        "size_kb": round(obj['size'] / 1024, 1),
                        "last_modified": obj['last_modified']
                    })

        return {
            "program": program,
            "documents": documents,
            "total_documents": len(documents),
            "source": "SharePoint GCC High (S3)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "SharePoint GCC High (S3)"}
