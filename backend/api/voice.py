"""
Voice Pipeline API endpoints
Handle audio upload, transcription, and Small Factory chain execution
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import json
import asyncio

from services.transcribe import get_transcribe_service, TranscriptionStatus
from services.small_factory import get_factory_engine, FactoryResult, FactoryStatus
from services.cosmos import CosmosService
from services.factory_handlers import get_registration_status
from core.config import settings

router = APIRouter()

# Register all Small Factory handlers on module load
_handler_status = get_registration_status()
db = CosmosService(getattr(settings, 'TABLE_VOICE_JOBS', 'apex-voice-jobs'))
transcribe_service = get_transcribe_service()
factory_engine = get_factory_engine()


# WebSocket connections for real-time updates
class VoiceConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_update(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json(data)
            except Exception:
                self.disconnect(job_id)


ws_manager = VoiceConnectionManager()


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    chain_id: str = Query("insurance_claim_from_call", description="Factory chain to execute"),
    auto_process: bool = Query(True, description="Automatically start processing after upload")
):
    """
    Upload an audio file for processing.

    Accepts MP3, WAV, M4A, FLAC formats.
    Optionally starts transcription and factory chain automatically.
    """
    # Validate file type
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/flac', 'audio/mp3']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    job_id = f"voice-{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    # In production, upload to S3
    # For now, we'll simulate with mock data
    s3_uri = f"s3://apex-audio/uploads/{job_id}/{file.filename}"

    # Create job record
    job_data = {
        "job_id": job_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "audio_s3_uri": s3_uri,
        "chain_id": chain_id,
        "status": "uploaded",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    await db.put_item(job_data)

    result = {
        "job_id": job_id,
        "status": "uploaded",
        "filename": file.filename,
        "s3_uri": s3_uri,
        "chain_id": chain_id,
        "message": "Audio uploaded successfully"
    }

    # Auto-start processing if requested
    if auto_process:
        # Start async processing
        asyncio.create_task(process_voice_job(job_id))
        result["status"] = "processing"
        result["message"] = "Audio uploaded and processing started"

    return result


@router.post("/transcribe/{job_id}")
async def start_transcription(job_id: str):
    """
    Start transcription for an uploaded audio file.
    """
    job = await db.get_item({"job_id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    # Start transcription
    result = await transcribe_service.start_transcription(
        audio_s3_uri=job['audio_s3_uri'],
        job_name=f"transcribe-{job_id}",
        enable_diarization=True
    )

    # Update job
    await db.update_item(
        {"job_id": job_id},
        {
            "transcribe_job_id": result['job_id'],
            "status": "transcribing",
            "updated_at": datetime.utcnow().isoformat()
        }
    )

    return {
        "job_id": job_id,
        "transcribe_job_id": result['job_id'],
        "status": "transcribing"
    }


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the current status of a voice processing job.
    """
    job = await db.get_item({"job_id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return {
        "job_id": job_id,
        "status": job.get('status'),
        "current_factory": job.get('current_factory'),
        "progress": job.get('progress', {}),
        "created_at": job.get('created_at'),
        "updated_at": job.get('updated_at'),
        "completed_at": job.get('completed_at'),
    }


@router.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """
    Get the full results of a completed voice processing job.
    """
    job = await db.get_item({"job_id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if job.get('status') not in ['completed', 'partial']:
        return {
            "job_id": job_id,
            "status": job.get('status'),
            "message": "Job not yet completed"
        }

    return {
        "job_id": job_id,
        "status": job.get('status'),
        "transcript": job.get('transcript'),
        "factory_results": job.get('factory_results', {}),
        "outputs": job.get('outputs', {}),
        "created_at": job.get('created_at'),
        "completed_at": job.get('completed_at'),
    }


@router.post("/process/{job_id}")
async def process_job(
    job_id: str,
    chain_id: Optional[str] = Query(None, description="Override the chain to execute")
):
    """
    Start or restart factory chain processing for a job.
    """
    job = await db.get_item({"job_id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    # Use provided chain or job's default
    chain = chain_id or job.get('chain_id', 'insurance_claim_from_call')

    # Start async processing
    asyncio.create_task(process_voice_job(job_id, chain))

    return {
        "job_id": job_id,
        "status": "processing",
        "chain_id": chain,
        "message": "Processing started"
    }


@router.websocket("/stream/{job_id}")
async def websocket_stream(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time processing updates.
    """
    await ws_manager.connect(job_id, websocket)

    try:
        while True:
            # Keep connection alive, updates sent via process_voice_job
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(job_id)


@router.get("/chains")
async def list_chains():
    """
    List all available factory chains.
    """
    return {
        "chains": factory_engine.list_chains()
    }


@router.get("/chains/{chain_id}")
async def get_chain(chain_id: str):
    """
    Get details of a specific factory chain.
    """
    chain = factory_engine.get_chain(chain_id)
    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chain {chain_id} not found"
        )

    return {
        "id": chain_id,
        "name": chain.name,
        "description": chain.description,
        "factories": [
            {
                "id": f.id,
                "action": f.action,
                "depends_on": f.depends_on,
                "config": f.config
            }
            for f in chain.factories
        ],
        "outputs": chain.outputs
    }


# Background processing function
async def process_voice_job(job_id: str, chain_id: Optional[str] = None):
    """
    Background task to process a voice job through the factory chain.
    """
    try:
        job = await db.get_item({"job_id": job_id})
        if not job:
            return

        chain = chain_id or job.get('chain_id', 'insurance_claim_from_call')

        # Update status
        await db.update_item(
            {"job_id": job_id},
            {
                "status": "processing",
                "chain_id": chain,
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        # Send WebSocket update
        await ws_manager.send_update(job_id, {
            "type": "status",
            "status": "processing",
            "chain_id": chain
        })

        # Step 1: Transcribe
        await db.update_item(
            {"job_id": job_id},
            {"current_factory": "transcribe"}
        )
        await ws_manager.send_update(job_id, {
            "type": "factory_start",
            "factory_id": "transcribe"
        })

        transcribe_result = await transcribe_service.wait_for_completion(
            f"transcribe-{job_id}"
        )

        if transcribe_result.get('status') == 'not_found':
            # Start transcription if not already started
            await transcribe_service.start_transcription(
                audio_s3_uri=job['audio_s3_uri'],
                job_name=f"transcribe-{job_id}"
            )
            transcribe_result = await transcribe_service.wait_for_completion(
                f"transcribe-{job_id}"
            )

        transcript = transcribe_result.get('transcript', {})

        await ws_manager.send_update(job_id, {
            "type": "factory_complete",
            "factory_id": "transcribe",
            "output": {"word_count": transcript.get('word_count', 0)}
        })

        # Update with transcript
        await db.update_item(
            {"job_id": job_id},
            {
                "transcript": transcript,
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        # Step 2: Execute factory chain
        def progress_callback(factory_id: str, result: FactoryResult):
            asyncio.create_task(ws_manager.send_update(job_id, {
                "type": "factory_update",
                "factory_id": factory_id,
                "status": result.status.value,
                "duration_ms": result.duration_ms
            }))

        chain_result = await factory_engine.execute_chain(
            chain_id=chain,
            initial_input={
                "transcript": transcript,
                "audio_s3_uri": job.get('audio_s3_uri'),
                "job_id": job_id
            },
            progress_callback=progress_callback
        )

        # Update with final results
        await db.update_item(
            {"job_id": job_id},
            {
                "status": "completed",
                "factory_results": chain_result.get('results', {}),
                "outputs": chain_result.get('outputs', {}),
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        await ws_manager.send_update(job_id, {
            "type": "completed",
            "status": "completed",
            "outputs": chain_result.get('outputs', {})
        })

    except Exception as e:
        # Update with error
        await db.update_item(
            {"job_id": job_id},
            {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        await ws_manager.send_update(job_id, {
            "type": "error",
            "status": "failed",
            "error": str(e)
        })


# Demo endpoint for testing without actual audio
@router.post("/demo/process")
async def demo_process(
    chain_id: str = Query("insurance_claim_from_call"),
    scenario: str = Query("insurance_claim", description="Demo scenario: insurance_claim, quality_check")
):
    """
    Process a demo call without uploading audio.
    Uses pre-built sample transcripts for demonstration.
    """
    job_id = f"demo-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()

    # Create demo job
    job_data = {
        "job_id": job_id,
        "filename": "demo_call.mp3",
        "audio_s3_uri": f"s3://apex-audio/demo/{scenario}.mp3",
        "chain_id": chain_id,
        "status": "processing",
        "is_demo": True,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    await db.put_item(job_data)

    # Process in background
    asyncio.create_task(process_voice_job(job_id, chain_id))

    return {
        "job_id": job_id,
        "status": "processing",
        "chain_id": chain_id,
        "scenario": scenario,
        "message": "Demo processing started. Poll /status/{job_id} for updates."
    }
