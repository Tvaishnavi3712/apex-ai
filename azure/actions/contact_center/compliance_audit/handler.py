"""
Compliance Audit - Small Factory
Audits conversation for compliance with required procedures.
"""

from typing import Dict, Any, List
import re
from services.small_factory import register_factory


# Compliance checklists by type
COMPLIANCE_RULES = {
    "insurance_call_compliance": {
        "proper_greeting": {
            "description": "Agent greeted customer professionally",
            "positive_patterns": [
                r"thank\s+you\s+for\s+calling",
                r"how\s+(?:can|may)\s+I\s+help",
                r"good\s+(?:morning|afternoon|evening)",
                r"welcome\s+to",
            ],
            "weight": 1.0,
        },
        "identity_verification": {
            "description": "Agent verified customer identity",
            "positive_patterns": [
                r"verify\s+your\s+(?:identity|information)",
                r"(?:policy|account)\s+number",
                r"last\s+(?:four|4)\s+(?:digits|numbers)",
                r"date\s+of\s+birth",
                r"confirm\s+your\s+(?:name|address)",
            ],
            "weight": 1.5,
        },
        "empathy_shown": {
            "description": "Agent showed empathy and understanding",
            "positive_patterns": [
                r"I\s+understand",
                r"I['\u2019]m\s+sorry\s+(?:to\s+hear|about)",
                r"that\s+must\s+be\s+(?:difficult|frustrating|hard)",
                r"I\s+(?:can\s+)?imagine",
                r"let\s+me\s+help",
            ],
            "weight": 1.0,
        },
        "accurate_information": {
            "description": "Agent provided accurate claim information",
            "positive_patterns": [
                r"your\s+claim\s+(?:number|status)",
                r"(?:next\s+)?steps?\s+(?:will\s+be|are)",
                r"you\s+(?:can|will)\s+expect",
                r"timeline\s+(?:is|for)",
            ],
            "weight": 1.5,
        },
        "proper_closing": {
            "description": "Agent closed call professionally",
            "positive_patterns": [
                r"anything\s+else\s+I\s+can\s+help",
                r"is\s+there\s+anything\s+else",
                r"thank\s+you\s+for\s+(?:calling|your\s+time)",
                r"have\s+a\s+(?:great|good|nice)\s+day",
            ],
            "weight": 1.0,
        },
        "no_prohibited_language": {
            "description": "No prohibited or inappropriate language used",
            "negative_patterns": [
                r"(?:guarantee|promise)\s+(?:you|that)",
                r"don['\u2019]t\s+worry\s+about\s+(?:it|that)",
                r"(?:stupid|dumb|idiot)",
                r"(?:definitely|certainly)\s+(?:will|won['\u2019]t)",
                r"no\s+problem\s+at\s+all",  # Soft prohibition
            ],
            "weight": 1.5,
        },
    },
    "contact_center_qa": {
        "professional_tone": {
            "description": "Maintained professional tone throughout",
            "positive_patterns": [
                r"please",
                r"thank\s+you",
                r"I\s+(?:would\s+be\s+happy|am\s+happy)\s+to",
            ],
            "weight": 1.0,
        },
        "active_listening": {
            "description": "Demonstrated active listening",
            "positive_patterns": [
                r"I\s+understand\s+(?:that|what)",
                r"so\s+(?:you['\u2019]re\s+saying|what\s+I\s+hear)",
                r"let\s+me\s+make\s+sure\s+I\s+understand",
                r"to\s+clarify",
            ],
            "weight": 1.0,
        },
        "resolution_offered": {
            "description": "Offered resolution or next steps",
            "positive_patterns": [
                r"(?:here['\u2019]s\s+)?what\s+(?:I\s+can|we\s+can)\s+do",
                r"let\s+me\s+(?:help|assist)",
                r"I['\u2019]ll\s+(?:take\s+care|handle)",
                r"next\s+step",
            ],
            "weight": 1.5,
        },
    },
}


def evaluate_rule(text: str, rule: Dict[str, Any], speaker_segments: List[Dict]) -> Dict[str, Any]:
    """Evaluate a single compliance rule."""
    agent_text = " ".join(
        seg.get('text', '') for seg in speaker_segments
        if 'agent' in seg.get('speaker', '').lower()
    )

    # Use agent text if available, otherwise full text
    search_text = agent_text if agent_text else text

    positive_patterns = rule.get('positive_patterns', [])
    negative_patterns = rule.get('negative_patterns', [])

    # Check positive patterns (should be present)
    positive_matches = []
    for pattern in positive_patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        positive_matches.extend(matches)

    # Check negative patterns (should be absent)
    negative_matches = []
    for pattern in negative_patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        negative_matches.extend(matches)

    # Determine pass/fail
    if negative_patterns and not positive_patterns:
        # Rule is about absence of bad things
        passed = len(negative_matches) == 0
        score = 1.0 if passed else 0.0
    elif positive_patterns and not negative_patterns:
        # Rule is about presence of good things
        passed = len(positive_matches) > 0
        score = min(len(positive_matches) * 0.5, 1.0)
    else:
        # Both types
        positive_score = min(len(positive_matches) * 0.5, 1.0)
        negative_penalty = len(negative_matches) * 0.3
        score = max(0, positive_score - negative_penalty)
        passed = score >= 0.5

    return {
        "passed": passed,
        "score": round(score, 2),
        "positive_matches": positive_matches[:3] if positive_matches else [],
        "negative_matches": negative_matches[:3] if negative_matches else [],
        "description": rule.get('description', ''),
        "weight": rule.get('weight', 1.0)
    }


@register_factory("compliance_audit")
async def compliance_audit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit conversation for compliance with required procedures.

    Input:
        diarize.segments: Labeled conversation segments
        config.checklist: Compliance checklist to use
        config.rules: Specific rules to check

    Output:
        overall_score: Compliance score (0-100)
        passed: Whether overall compliance passed
        rule_results: Results for each rule
        violations: List of violations
        recommendations: Improvement recommendations
    """
    config = input_data.get('config', {})
    diarize_output = input_data.get('diarize', {})
    transcribe_output = input_data.get('transcribe', {})
    state = input_data.get('state', {})

    # Get text and segments
    segments = diarize_output.get('segments', [])
    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    checklist_name = config.get('checklist', 'insurance_call_compliance')
    specific_rules = config.get('rules', [])

    # Get compliance rules
    checklist = COMPLIANCE_RULES.get(checklist_name, COMPLIANCE_RULES['insurance_call_compliance'])

    # Filter to specific rules if provided
    if specific_rules:
        checklist = {k: v for k, v in checklist.items() if k in specific_rules}

    # Evaluate each rule
    rule_results = {}
    violations = []
    total_score = 0
    total_weight = 0

    for rule_name, rule_def in checklist.items():
        result = evaluate_rule(full_text, rule_def, segments)
        rule_results[rule_name] = result

        weight = result['weight']
        total_weight += weight
        total_score += result['score'] * weight

        if not result['passed']:
            violations.append({
                "rule": rule_name,
                "description": result['description'],
                "severity": "high" if weight > 1.0 else "medium",
                "evidence": result.get('negative_matches', [])
            })

    # Calculate overall score
    overall_score = round((total_score / total_weight * 100) if total_weight > 0 else 0, 1)
    passed = overall_score >= 70 and len([v for v in violations if v['severity'] == 'high']) == 0

    # Generate recommendations
    recommendations = []
    for violation in violations:
        if violation['rule'] == 'proper_greeting':
            recommendations.append("Start calls with a warm, professional greeting")
        elif violation['rule'] == 'identity_verification':
            recommendations.append("Always verify customer identity before discussing account details")
        elif violation['rule'] == 'empathy_shown':
            recommendations.append("Express understanding and empathy when customers share concerns")
        elif violation['rule'] == 'proper_closing':
            recommendations.append("End calls by asking if there's anything else and thanking the customer")
        elif violation['rule'] == 'no_prohibited_language':
            recommendations.append("Avoid making guarantees or promises about outcomes")

    return {
        "overall_score": overall_score,
        "passed": passed,
        "checklist_used": checklist_name,
        "rule_results": rule_results,
        "violations": violations,
        "violation_count": len(violations),
        "recommendations": recommendations,
        "rules_checked": len(rule_results),
        "rules_passed": len([r for r in rule_results.values() if r['passed']])
    }
