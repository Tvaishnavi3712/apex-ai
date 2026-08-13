"""
Diarize Speakers - Small Factory
Labels speakers in transcript segments with human-readable names.
"""

from typing import Dict, Any, List
from services.small_factory import register_factory


@register_factory("diarize_speakers")
async def diarize_speakers(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply human-readable labels to speaker segments.

    Input:
        transcribe.segments: Segments with speaker labels (spk_0, spk_1, etc.)
        config.speaker_labels: Mapping of speaker IDs to names

    Output:
        segments: Segments with human-readable speaker names
        speakers: List of speaker info with roles
        agent_segments: Segments where agent is speaking
        customer_segments: Segments where customer is speaking
        conversation_flow: Alternating speaker pattern analysis
    """
    config = input_data.get('config', {})
    transcribe_output = input_data.get('transcribe', {})

    segments = transcribe_output.get('segments', [])
    raw_speakers = transcribe_output.get('speakers', [])

    # Get speaker label mapping
    speaker_labels = config.get('speaker_labels', {})

    # Default mapping if not provided
    if not speaker_labels:
        speaker_labels = {
            'spk_0': 'Agent',
            'spk_1': 'Customer',
            'spk_2': 'Customer 2',
            'unknown': 'Unknown'
        }

    # Apply labels to segments
    labeled_segments = []
    agent_segments = []
    customer_segments = []

    for segment in segments:
        raw_speaker = segment.get('speaker', 'unknown')
        labeled_speaker = speaker_labels.get(raw_speaker, raw_speaker)

        labeled_segment = {
            **segment,
            'speaker': labeled_speaker,
            'speaker_id': raw_speaker
        }
        labeled_segments.append(labeled_segment)

        # Categorize by role
        if 'Agent' in labeled_speaker:
            agent_segments.append(labeled_segment)
        else:
            customer_segments.append(labeled_segment)

    # Build speaker info
    speakers = []
    for raw_id in raw_speakers:
        label = speaker_labels.get(raw_id, raw_id)
        speaker_segs = [s for s in labeled_segments if s['speaker_id'] == raw_id]

        # Calculate talk time
        talk_time = sum(s['end_time'] - s['start_time'] for s in speaker_segs)

        speakers.append({
            'id': raw_id,
            'name': label,
            'role': 'agent' if 'Agent' in label else 'customer',
            'segment_count': len(speaker_segs),
            'talk_time_seconds': round(talk_time, 2),
            'word_count': sum(len(s['text'].split()) for s in speaker_segs)
        })

    # Analyze conversation flow
    conversation_flow = analyze_conversation_flow(labeled_segments)

    return {
        "segments": labeled_segments,
        "speakers": speakers,
        "agent_segments": agent_segments,
        "customer_segments": customer_segments,
        "conversation_flow": conversation_flow,
        "total_segments": len(labeled_segments)
    }


def analyze_conversation_flow(segments: List[Dict]) -> Dict[str, Any]:
    """Analyze the flow of conversation between speakers."""
    if not segments:
        return {"pattern": "empty", "turn_count": 0}

    turns = []
    current_speaker = None
    current_turn_start = None

    for seg in segments:
        if seg['speaker'] != current_speaker:
            if current_speaker is not None:
                turns.append({
                    'speaker': current_speaker,
                    'start': current_turn_start,
                    'end': seg['start_time']
                })
            current_speaker = seg['speaker']
            current_turn_start = seg['start_time']

    # Add final turn
    if current_speaker and segments:
        turns.append({
            'speaker': current_speaker,
            'start': current_turn_start,
            'end': segments[-1]['end_time']
        })

    # Calculate metrics
    avg_turn_duration = sum(t['end'] - t['start'] for t in turns) / len(turns) if turns else 0

    return {
        "turn_count": len(turns),
        "avg_turn_duration_seconds": round(avg_turn_duration, 2),
        "first_speaker": turns[0]['speaker'] if turns else None,
        "last_speaker": turns[-1]['speaker'] if turns else None,
        "turns": turns
    }
