"""
Transcribe Audio - Small Factory
Converts audio to text using AWS Transcribe with speaker diarization.
"""

from typing import Dict, Any
from services.transcribe import get_transcribe_service
from services.small_factory import register_factory


@register_factory("transcribe_audio")
async def transcribe_audio(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transcribe audio file to text.

    Input:
        initial_input.audio_s3_uri: S3 URI of audio file
        config.language: Language code (default: en-US)
        config.enable_diarization: Enable speaker labels (default: true)

    Output:
        full_text: Complete transcript
        segments: Speaker-labeled segments with timestamps
        speakers: List of unique speakers
        word_count: Total word count
        duration_seconds: Audio duration
    """
    config = input_data.get('config', {})
    initial = input_data.get('initial_input', {})

    audio_uri = initial.get('audio_s3_uri')
    if not audio_uri:
        return {"error": "No audio_s3_uri provided"}

    language = config.get('language', 'en-US')
    enable_diarization = config.get('enable_diarization', True)
    max_speakers = config.get('max_speakers', 2)

    # Get transcribe service
    service = get_transcribe_service()

    # Start and wait for transcription
    job_name = f"factory-{initial.get('job_id', 'unknown')}"

    result = await service.start_transcription(
        audio_s3_uri=audio_uri,
        job_name=job_name,
        language_code=language,
        enable_diarization=enable_diarization,
        max_speakers=max_speakers
    )

    # Wait for completion and get transcript
    final_result = await service.wait_for_completion(job_name)

    if final_result.get('status') == 'completed':
        transcript = final_result.get('transcript', {})
        return {
            "full_text": transcript.get('full_text', ''),
            "segments": transcript.get('segments', []),
            "speakers": transcript.get('speakers', []),
            "word_count": transcript.get('word_count', 0),
            "duration_seconds": transcript.get('duration_seconds', 0),
            "segment_count": transcript.get('segment_count', 0),
        }
    else:
        return {
            "error": final_result.get('failure_reason', 'Transcription failed'),
            "status": final_result.get('status')
        }
