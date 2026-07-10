"""
Bedrock Claude Service - Invoke Claude models for AI-powered factory processing.
Provides intelligent analysis for contact center and insurance underwriting factories.
"""
import boto3
import json
import structlog
from typing import Dict, Any, Optional, List
from botocore.config import Config

logger = structlog.get_logger()


class BedrockClaudeService:
    """Service for invoking Claude models via AWS Bedrock."""

    # Available Claude models on Bedrock
    MODELS = {
        "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
        "claude-instant": "anthropic.claude-instant-v1",
    }

    # Default model for factory operations (balanced cost/performance)
    DEFAULT_MODEL = "claude-3-sonnet"

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        config = Config(
            retries={"max_attempts": 3, "mode": "adaptive"},
            connect_timeout=30,
            read_timeout=120,
        )
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=config
        )

    async def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke Claude model with a prompt.

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            model: Model to use (default: claude-3-sonnet)
            max_tokens: Maximum response tokens
            temperature: Response randomness (0.0-1.0)
            context: Additional context to include

        Returns:
            Dict with response, usage, and metadata
        """
        model_id = self.MODELS.get(model, self.MODELS[self.DEFAULT_MODEL])

        # Build message structure
        messages = [{"role": "user", "content": prompt}]

        # Add context to prompt if provided
        if context:
            context_str = json.dumps(context, indent=2)
            messages[0]["content"] = f"Context:\n```json\n{context_str}\n```\n\n{prompt}"

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system_prompt:
            request_body["system"] = system_prompt

        try:
            logger.debug("Invoking Bedrock Claude", model=model_id)

            response = self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())

            # Extract content from response
            content = ""
            if response_body.get("content"):
                content = response_body["content"][0].get("text", "")

            return {
                "success": True,
                "response": content,
                "model": model_id,
                "usage": {
                    "input_tokens": response_body.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": response_body.get("usage", {}).get("output_tokens", 0),
                },
                "stop_reason": response_body.get("stop_reason"),
            }

        except Exception as e:
            logger.error("Bedrock Claude invocation failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "model": model_id,
            }

    async def analyze_conversation(
        self,
        transcript: str,
        analysis_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a conversation transcript using Claude.

        Args:
            transcript: The conversation transcript
            analysis_type: Type of analysis (summary, sentiment, claims, fraud, coaching)
            context: Additional context (playbook rules, etc.)

        Returns:
            Analysis results as structured JSON
        """
        system_prompts = {
            "summary": self._get_summary_system_prompt(),
            "sentiment": self._get_sentiment_system_prompt(),
            "claims": self._get_claims_system_prompt(),
            "fraud": self._get_fraud_system_prompt(),
            "coaching": self._get_coaching_system_prompt(),
        }

        user_prompts = {
            "summary": self._get_summary_user_prompt(transcript, context),
            "sentiment": self._get_sentiment_user_prompt(transcript, context),
            "claims": self._get_claims_user_prompt(transcript, context),
            "fraud": self._get_fraud_user_prompt(transcript, context),
            "coaching": self._get_coaching_user_prompt(transcript, context),
        }

        system_prompt = system_prompts.get(analysis_type)
        user_prompt = user_prompts.get(analysis_type)

        if not system_prompt or not user_prompt:
            return {
                "success": False,
                "error": f"Unknown analysis type: {analysis_type}",
                "response": None,
            }

        result = await self.invoke(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,  # Lower temp for structured analysis
        )

        if result["success"]:
            # Try to parse JSON from response
            try:
                parsed = self._extract_json(result["response"])
                result["parsed"] = parsed
            except Exception:
                result["parsed"] = None

        return result

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response."""
        # Try to find JSON block
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try parsing the whole response
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)

        # Try finding JSON object anywhere
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])

        raise ValueError("No JSON found in response")

    # System prompts for different analysis types

    def _get_summary_system_prompt(self) -> str:
        return """You are an expert contact center analyst specializing in insurance claims processing.
Your task is to generate comprehensive, accurate summaries of customer calls.

Focus on:
- Key facts and decisions made
- Action items and next steps
- Customer concerns and resolutions
- Compliance-relevant information

Always respond with valid JSON matching the required schema."""

    def _get_sentiment_system_prompt(self) -> str:
        return """You are an expert conversation analyst specializing in sentiment analysis.
Your task is to analyze the emotional tone and sentiment throughout a conversation.

Analyze:
- Overall sentiment (positive, negative, neutral, mixed)
- Sentiment arc (improving, declining, stable, volatile)
- Key emotional moments and triggers
- Per-speaker sentiment breakdown

Always respond with valid JSON matching the required schema."""

    def _get_claims_system_prompt(self) -> str:
        return """You are an expert insurance claims analyst.
Your task is to extract claim details from customer conversations.

Extract:
- Claim type (auto, home, health, life, other)
- Incident details (date, location, description)
- Policy information
- Damage amounts and estimates
- Missing information

Always respond with valid JSON matching the required schema."""

    def _get_fraud_system_prompt(self) -> str:
        return """You are an expert fraud detection analyst for insurance claims.
Your task is to identify potential fraud indicators in customer conversations.

Look for:
- Inconsistent stories or changing details
- Reluctance to provide information
- Excessive or suspicious claims
- Red flag language patterns
- Timeline inconsistencies

Rate fraud risk on a 0-100 scale and provide detailed reasoning.
Always respond with valid JSON matching the required schema."""

    def _get_coaching_system_prompt(self) -> str:
        return """You are an expert contact center coach and trainer.
Your task is to analyze agent performance and provide actionable coaching tips.

Evaluate:
- Communication skills
- Empathy and rapport building
- Process adherence
- Problem resolution effectiveness
- Compliance with required procedures

Provide specific, actionable improvement suggestions.
Always respond with valid JSON matching the required schema."""

    # User prompts for different analysis types

    def _get_summary_user_prompt(self, transcript: str, context: Optional[Dict] = None) -> str:
        context_str = ""
        if context:
            if context.get("claim_data"):
                context_str = f"\n\nExtracted claim data:\n{json.dumps(context['claim_data'], indent=2)}"
            if context.get("compliance_data"):
                context_str += f"\n\nCompliance results:\n{json.dumps(context['compliance_data'], indent=2)}"

        return f"""Analyze this insurance claim conversation and generate a summary.
{context_str}

Transcript:
{transcript}

Respond with JSON in this format:
{{
  "summary": "2-3 sentence executive summary",
  "claim_type": "auto|home|health|life|other",
  "requires_followup": true/false,
  "key_facts": ["fact 1", "fact 2", ...],
  "action_items": ["action 1", "action 2", ...],
  "customer_concern_resolved": true/false,
  "next_steps": "description of next steps"
}}"""

    def _get_sentiment_user_prompt(self, transcript: str, context: Optional[Dict] = None) -> str:
        return f"""Analyze the sentiment throughout this conversation.

Transcript:
{transcript}

Respond with JSON in this format:
{{
  "overall_sentiment": "positive|negative|neutral|mixed",
  "average_score": 0.0 to 1.0 (0=very negative, 1=very positive),
  "sentiment_arc": "improving|declining|stable|volatile",
  "timeline": [
    {{"segment_index": 0, "sentiment": "positive", "score": 0.8, "speaker": "Customer", "key_phrase": "phrase"}},
    ...
  ],
  "by_speaker": {{
    "Agent": {{"average_score": 0.8, "sentiment": "positive"}},
    "Customer": {{"average_score": 0.6, "sentiment": "neutral"}}
  }},
  "emotional_peaks": [
    {{"type": "positive|negative", "segment_index": 5, "trigger": "resolution offered"}}
  ],
  "key_observations": ["observation 1", "observation 2"]
}}"""

    def _get_claims_user_prompt(self, transcript: str, context: Optional[Dict] = None) -> str:
        entities_str = ""
        if context and context.get("entities"):
            entities_str = f"\n\nPreviously extracted entities:\n{json.dumps(context['entities'], indent=2)}"

        return f"""Extract insurance claim details from this conversation.
{entities_str}

Transcript:
{transcript}

Respond with JSON in this format:
{{
  "claim_type": "auto|home|health|life|other",
  "claim_type_confidence": 0.0 to 1.0,
  "completeness_score": 0 to 100,
  "is_actionable": true/false,
  "requires_callback": true/false,
  "missing_fields": ["field1", "field2"],
  "extracted_entities": {{
    "policy_number": "...",
    "claim_number": "...",
    "claimant_name": "...",
    "incident_date": "...",
    "incident_type": "...",
    "damage_amount": "...",
    "location": "...",
    "vehicle": "...",
    "description": "..."
  }},
  "confidence_scores": {{
    "policy_number": 0.95,
    "incident_date": 0.85,
    ...
  }}
}}"""

    def _get_fraud_user_prompt(self, transcript: str, context: Optional[Dict] = None) -> str:
        context_str = ""
        if context:
            if context.get("claim_data"):
                context_str = f"\n\nClaim data:\n{json.dumps(context['claim_data'], indent=2)}"
            if context.get("sentiment_data"):
                context_str += f"\n\nSentiment analysis:\n{json.dumps(context['sentiment_data'], indent=2)}"
            if context.get("fraud_indicators"):
                context_str += f"\n\nKnown fraud indicators to check:\n{json.dumps(context['fraud_indicators'], indent=2)}"

        return f"""Analyze this conversation for potential fraud indicators.
{context_str}

Transcript:
{transcript}

Respond with JSON in this format:
{{
  "fraud_score": 0 to 100 (higher = more suspicious),
  "risk_level": "low|medium|high|critical",
  "exceeds_threshold": true/false (threshold is 70),
  "requires_review": true/false,
  "indicator_count": number,
  "indicators_detected": [
    {{
      "indicator": "inconsistent_story",
      "description": "What was detected",
      "evidence": ["quote 1", "quote 2"],
      "weight": 0 to 30
    }},
    ...
  ],
  "recommendation": "approve|review|investigate|escalate",
  "reasoning": "Overall assessment explanation",
  "confidence": 0.0 to 1.0
}}"""

    def _get_coaching_user_prompt(self, transcript: str, context: Optional[Dict] = None) -> str:
        context_str = ""
        if context:
            if context.get("compliance_data"):
                context_str = f"\n\nCompliance audit results:\n{json.dumps(context['compliance_data'], indent=2)}"
            if context.get("sentiment_data"):
                context_str += f"\n\nSentiment analysis:\n{json.dumps(context['sentiment_data'], indent=2)}"

        return f"""Analyze this conversation and provide agent coaching recommendations.
{context_str}

Transcript:
{transcript}

Respond with JSON in this format:
{{
  "coaching_priority": "high|medium|low",
  "requires_followup": true/false,
  "tip_count": number,
  "tips": [
    {{
      "area": "empathy|compliance|communication|efficiency|knowledge",
      "tip": "Specific actionable tip",
      "priority": "high|medium|low",
      "description": "Why this matters and how to improve",
      "example": "Example of better phrasing/approach"
    }},
    ...
  ],
  "priority_areas": ["area 1", "area 2"],
  "strengths": ["strength 1", "strength 2"],
  "training_modules": [
    {{
      "module_id": "EMP-101",
      "title": "Module title",
      "duration_minutes": 30,
      "reason": "Why recommended"
    }}
  ],
  "overall_performance_score": 0 to 100
}}"""


# Singleton instance
_service_instance: Optional[BedrockClaudeService] = None


def get_bedrock_claude_service(region: str = "us-east-1") -> BedrockClaudeService:
    """Get or create the Bedrock Claude service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BedrockClaudeService(region=region)
    return _service_instance
