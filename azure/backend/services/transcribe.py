"""
AWS Transcribe Service
Handles audio transcription with speaker diarization
"""

import boto3
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import structlog

from core.config import settings

logger = structlog.get_logger()


class TranscriptionStatus(str, Enum):
    """Transcription job status"""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscribeService:
    """
    AWS Transcribe integration for converting audio to text.
    Supports speaker diarization, custom vocabularies, and real-time updates.
    """

    def __init__(self):
        self.client = boto3.client(
            'transcribe',
            region_name=settings.AZURE_LOCATION
        )
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AZURE_LOCATION
        )
        self.output_bucket = getattr(settings, 'TRANSCRIBE_OUTPUT_BUCKET', 'apex-transcripts')

    async def start_transcription(
        self,
        audio_s3_uri: str,
        job_name: Optional[str] = None,
        language_code: str = "en-US",
        enable_diarization: bool = True,
        max_speakers: int = 2,
        vocabulary_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start an async transcription job.

        Args:
            audio_s3_uri: blob URI of the audio file (s3://bucket/key)
            job_name: Optional custom job name
            language_code: Language code (default: en-US)
            enable_diarization: Enable speaker identification
            max_speakers: Maximum number of speakers to identify
            vocabulary_name: Custom vocabulary for industry terms

        Returns:
            Job details including job_id and status
        """
        if not job_name:
            job_name = f"apex-transcribe-{uuid.uuid4().hex[:8]}"

        try:
            # Build transcription settings
            settings_config = {
                'ShowSpeakerLabels': enable_diarization,
                'MaxSpeakerLabels': max_speakers if enable_diarization else 2,
            }

            # Build job parameters
            job_params = {
                'TranscriptionJobName': job_name,
                'Media': {'MediaFileUri': audio_s3_uri},
                'LanguageCode': language_code,
                'OutputBucketName': self.output_bucket,
                'OutputKey': f"transcripts/{job_name}.json",
                'Settings': settings_config,
            }

            # Add custom vocabulary if specified
            if vocabulary_name:
                job_params['Settings']['VocabularyName'] = vocabulary_name

            # Start the job
            response = await asyncio.to_thread(
                self.client.start_transcription_job,
                **job_params
            )

            job = response['TranscriptionJob']

            logger.info(
                "Transcription job started",
                job_name=job_name,
                audio_uri=audio_s3_uri
            )

            return {
                "job_id": job_name,
                "status": TranscriptionStatus.IN_PROGRESS.value,
                "audio_s3_uri": audio_s3_uri,
                "output_uri": f"s3://{self.output_bucket}/transcripts/{job_name}.json",
                "language_code": language_code,
                "diarization_enabled": enable_diarization,
                "created_at": datetime.utcnow().isoformat(),
            }

        except self.client.exceptions.ConflictException:
            # Job already exists
            return await self.get_job_status(job_name)

        except Exception as e:
            logger.error("Failed to start transcription", error=str(e))
            raise

    async def get_job_status(self, job_name: str) -> Dict[str, Any]:
        """
        Get the status of a transcription job.

        Args:
            job_name: The transcription job name/ID

        Returns:
            Job status and details
        """
        try:
            response = await asyncio.to_thread(
                self.client.get_transcription_job,
                TranscriptionJobName=job_name
            )

            job = response['TranscriptionJob']
            status_map = {
                'QUEUED': TranscriptionStatus.QUEUED,
                'IN_PROGRESS': TranscriptionStatus.IN_PROGRESS,
                'COMPLETED': TranscriptionStatus.COMPLETED,
                'FAILED': TranscriptionStatus.FAILED,
            }

            result = {
                "job_id": job_name,
                "status": status_map.get(job['TranscriptionJobStatus'], TranscriptionStatus.IN_PROGRESS).value,
                "created_at": job.get('CreationTime', '').isoformat() if job.get('CreationTime') else None,
                "completed_at": job.get('CompletionTime', '').isoformat() if job.get('CompletionTime') else None,
            }

            if job['TranscriptionJobStatus'] == 'COMPLETED':
                result['transcript_uri'] = job['Transcript']['TranscriptFileUri']

            if job['TranscriptionJobStatus'] == 'FAILED':
                result['failure_reason'] = job.get('FailureReason', 'Unknown error')

            return result

        except self.client.exceptions.NotFoundException:
            return {
                "job_id": job_name,
                "status": "not_found",
                "error": f"Job {job_name} not found"
            }
        except Exception as e:
            logger.error("Failed to get job status", job_name=job_name, error=str(e))
            raise

    async def get_transcript(self, job_name: str) -> Dict[str, Any]:
        """
        Get the transcript results for a completed job.

        Args:
            job_name: The transcription job name/ID

        Returns:
            Parsed transcript with segments and speaker labels
        """
        # First check if job is complete
        status = await self.get_job_status(job_name)

        if status['status'] != TranscriptionStatus.COMPLETED.value:
            return {
                "status": status['status'],
                "message": "Transcription not yet complete",
                "job_id": job_name
            }

        # Download transcript from S3
        try:
            transcript_key = f"transcripts/{job_name}.json"
            response = await asyncio.to_thread(
                self.s3_client.get_object,
                Bucket=self.output_bucket,
                Key=transcript_key
            )

            transcript_data = json.loads(response['Body'].read().decode('utf-8'))

            # Parse into structured format
            return self._parse_transcript(transcript_data)

        except Exception as e:
            logger.error("Failed to get transcript", job_name=job_name, error=str(e))
            raise

    def _parse_transcript(self, raw_transcript: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw AWS Transcribe output into structured format.

        Returns:
            Structured transcript with:
            - full_text: Complete transcript text
            - segments: List of speaker-labeled segments with timestamps
            - speakers: List of unique speakers
            - word_count: Total word count
            - duration_seconds: Audio duration
        """
        results = raw_transcript.get('results', {})

        # Get full transcript
        transcripts = results.get('transcripts', [])
        full_text = transcripts[0].get('transcript', '') if transcripts else ''

        # Parse speaker segments
        segments = []
        speaker_segments = results.get('speaker_labels', {}).get('segments', [])
        items = results.get('items', [])

        # Build word-to-speaker mapping
        word_speakers = {}
        for segment in speaker_segments:
            speaker = segment.get('speaker_label', 'unknown')
            for item in segment.get('items', []):
                start_time = item.get('start_time')
                if start_time:
                    word_speakers[start_time] = speaker

        # Group consecutive words by speaker
        current_segment = None
        for item in items:
            if item.get('type') == 'pronunciation':
                start_time = item.get('start_time', '0')
                end_time = item.get('end_time', '0')
                content = item.get('alternatives', [{}])[0].get('content', '')
                speaker = word_speakers.get(start_time, 'unknown')

                if current_segment and current_segment['speaker'] == speaker:
                    # Continue current segment
                    current_segment['text'] += ' ' + content
                    current_segment['end_time'] = float(end_time)
                else:
                    # Start new segment
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = {
                        'speaker': speaker,
                        'text': content,
                        'start_time': float(start_time),
                        'end_time': float(end_time),
                    }
            elif item.get('type') == 'punctuation' and current_segment:
                current_segment['text'] += item.get('alternatives', [{}])[0].get('content', '')

        # Add final segment
        if current_segment:
            segments.append(current_segment)

        # Get unique speakers
        speakers = list(set(s['speaker'] for s in segments))

        # Calculate duration
        duration = max(s['end_time'] for s in segments) if segments else 0

        return {
            "full_text": full_text,
            "segments": segments,
            "speakers": speakers,
            "word_count": len(full_text.split()),
            "duration_seconds": duration,
            "segment_count": len(segments),
        }

    async def wait_for_completion(
        self,
        job_name: str,
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> Dict[str, Any]:
        """
        Wait for a transcription job to complete.

        Args:
            job_name: The transcription job name/ID
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait

        Returns:
            Final job status and transcript if completed
        """
        start_time = datetime.utcnow()

        while True:
            status = await self.get_job_status(job_name)

            if status['status'] == TranscriptionStatus.COMPLETED.value:
                transcript = await self.get_transcript(job_name)
                return {
                    **status,
                    "transcript": transcript
                }

            if status['status'] == TranscriptionStatus.FAILED.value:
                return status

            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > max_wait:
                return {
                    "job_id": job_name,
                    "status": "timeout",
                    "error": f"Job did not complete within {max_wait} seconds"
                }

            await asyncio.sleep(poll_interval)

    async def delete_job(self, job_name: str) -> bool:
        """Delete a transcription job."""
        try:
            await asyncio.to_thread(
                self.client.delete_transcription_job,
                TranscriptionJobName=job_name
            )
            return True
        except Exception as e:
            logger.error("Failed to delete job", job_name=job_name, error=str(e))
            return False


# Mock implementation for local development
class MockTranscribeService(TranscribeService):
    """
    Mock Transcribe service for local development and demos.
    Returns realistic sample transcripts without calling AWS.
    """

    SAMPLE_TRANSCRIPTS = {
        "insurance_claim": {
            "full_text": "Thank you for calling Apex Insurance, my name is Sarah, how can I help you today? Hi Sarah, I need to file a claim for a car accident I was in yesterday. I'm so sorry to hear that. Are you okay? Were there any injuries? No, thankfully no one was hurt, but my car is pretty badly damaged. I was rear-ended at a stop light on Main Street. I understand how stressful that must be. Let me help you get this claim started right away. Can you give me your policy number? Yes, it's A-P-X-1-2-3-4-5-6. Perfect, I found your policy. I see you have comprehensive coverage. Can you tell me more about what happened? I was stopped at the red light at Main and Fifth Street around 3 PM yesterday. The driver behind me wasn't paying attention and hit me pretty hard. My bumper is completely crushed and the trunk won't close. That sounds like significant damage. Have you gotten any repair estimates yet? Not yet, I came straight home after the accident. I have the other driver's insurance information. That's great that you have their information. We'll need that for subrogation. I'm going to open this claim for you right now. Your claim number is C-L-M-2026-0001. A claims adjuster will contact you within 24 hours to schedule an inspection. Thank you so much Sarah, I really appreciate your help. You're welcome! Is there anything else I can help you with today? No, that's all I needed. Thank you again. You're welcome. Take care and drive safely!",
            "segments": [
                {"speaker": "spk_0", "text": "Thank you for calling Apex Insurance, my name is Sarah, how can I help you today?", "start_time": 0.0, "end_time": 4.5},
                {"speaker": "spk_1", "text": "Hi Sarah, I need to file a claim for a car accident I was in yesterday.", "start_time": 5.0, "end_time": 9.2},
                {"speaker": "spk_0", "text": "I'm so sorry to hear that. Are you okay? Were there any injuries?", "start_time": 9.8, "end_time": 13.5},
                {"speaker": "spk_1", "text": "No, thankfully no one was hurt, but my car is pretty badly damaged. I was rear-ended at a stop light on Main Street.", "start_time": 14.0, "end_time": 21.0},
                {"speaker": "spk_0", "text": "I understand how stressful that must be. Let me help you get this claim started right away. Can you give me your policy number?", "start_time": 21.5, "end_time": 28.0},
                {"speaker": "spk_1", "text": "Yes, it's A-P-X-1-2-3-4-5-6.", "start_time": 28.5, "end_time": 32.0},
                {"speaker": "spk_0", "text": "Perfect, I found your policy. I see you have comprehensive coverage. Can you tell me more about what happened?", "start_time": 32.5, "end_time": 39.0},
                {"speaker": "spk_1", "text": "I was stopped at the red light at Main and Fifth Street around 3 PM yesterday. The driver behind me wasn't paying attention and hit me pretty hard. My bumper is completely crushed and the trunk won't close.", "start_time": 39.5, "end_time": 52.0},
                {"speaker": "spk_0", "text": "That sounds like significant damage. Have you gotten any repair estimates yet?", "start_time": 52.5, "end_time": 57.0},
                {"speaker": "spk_1", "text": "Not yet, I came straight home after the accident. I have the other driver's insurance information.", "start_time": 57.5, "end_time": 63.0},
                {"speaker": "spk_0", "text": "That's great that you have their information. We'll need that for subrogation. I'm going to open this claim for you right now. Your claim number is C-L-M-2026-0001. A claims adjuster will contact you within 24 hours to schedule an inspection.", "start_time": 63.5, "end_time": 78.0},
                {"speaker": "spk_1", "text": "Thank you so much Sarah, I really appreciate your help.", "start_time": 78.5, "end_time": 82.0},
                {"speaker": "spk_0", "text": "You're welcome! Is there anything else I can help you with today?", "start_time": 82.5, "end_time": 86.0},
                {"speaker": "spk_1", "text": "No, that's all I needed. Thank you again.", "start_time": 86.5, "end_time": 89.0},
                {"speaker": "spk_0", "text": "You're welcome. Take care and drive safely!", "start_time": 89.5, "end_time": 92.0},
            ],
            "speakers": ["spk_0", "spk_1"],
            "word_count": 342,
            "duration_seconds": 92.0,
            "segment_count": 15,
        }
    }

    def __init__(self):
        self._jobs = {}

    async def start_transcription(
        self,
        audio_s3_uri: str,
        job_name: Optional[str] = None,
        language_code: str = "en-US",
        enable_diarization: bool = True,
        max_speakers: int = 2,
        vocabulary_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mock: Start a transcription job (completes immediately)."""
        if not job_name:
            job_name = f"apex-transcribe-{uuid.uuid4().hex[:8]}"

        self._jobs[job_name] = {
            "job_id": job_name,
            "status": TranscriptionStatus.COMPLETED.value,
            "audio_s3_uri": audio_s3_uri,
            "output_uri": f"s3://apex-transcripts/transcripts/{job_name}.json",
            "language_code": language_code,
            "diarization_enabled": enable_diarization,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }

        logger.info("Mock transcription job started", job_name=job_name)

        return self._jobs[job_name]

    async def get_job_status(self, job_name: str) -> Dict[str, Any]:
        """Mock: Get job status."""
        if job_name in self._jobs:
            return self._jobs[job_name]
        return {
            "job_id": job_name,
            "status": "not_found",
            "error": f"Job {job_name} not found"
        }

    async def get_transcript(self, job_name: str) -> Dict[str, Any]:
        """Mock: Get transcript (returns sample data)."""
        return self.SAMPLE_TRANSCRIPTS["insurance_claim"]

    async def wait_for_completion(
        self,
        job_name: str,
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> Dict[str, Any]:
        """Mock: Wait for completion (returns immediately)."""
        status = await self.get_job_status(job_name)
        transcript = await self.get_transcript(job_name)
        return {
            **status,
            "transcript": transcript
        }


# Factory function to get appropriate service
def get_transcribe_service() -> TranscribeService:
    """Get the appropriate transcribe service based on environment."""
    if getattr(settings, 'USE_MOCK_AWS', True):
        return MockTranscribeService()
    return TranscribeService()
