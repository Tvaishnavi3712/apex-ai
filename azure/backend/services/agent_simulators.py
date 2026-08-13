"""
Apex agent simulators — cloud-neutral demo reasoning engines.

Contains the in-process simulators, routing, and response shaping shared by
every Apex agent. No cloud SDK dependency: the concrete runtime
(`services/foundry_agent.py`) supplies `_invoke_runtime`.
"""
import json
import base64
import subprocess
import tempfile
import os
import re
import sys
import random
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, List


class CREUnderwritingKnowledgeBase:
    """Knowledge base for CRE Underwriting demo conversations."""

    # Sample processed deals for context
    PROCESSED_DEALS = {
        "CRE-2026-001-MUP": {
            "name": "Lakefront Development LLC - Mixed-Use Portfolio",
            "property_type": "Mixed-Use High-Rise",
            "location": "Chicago, IL",
            "tiv": 226000000,
            "locations": 3,
            "risk_score": 72,
            "risk_tier": "Moderate",
            "premium_estimate": 645000,
            "decision": "Refer to Senior Underwriter",
            "key_concerns": ["High-rise complexity", "Recent water damage claim", "Mixed occupancy"],
            "positive_factors": ["Fire resistive construction", "Full sprinkler coverage", "Strong tenant mix"],
            "loss_history": {"total_claims": 2, "total_paid": 312500, "open_claims": 0}
        },
        "CRE-2026-002-IND": {
            "name": "Midwest Industrial Partners - Industrial Portfolio",
            "property_type": "Industrial/Warehouse",
            "location": "Multiple Midwest locations",
            "tiv": 372300000,
            "locations": 5,
            "risk_score": 68,
            "risk_tier": "Acceptable",
            "premium_estimate": 892000,
            "decision": "Refer to Senior Underwriter",
            "key_concerns": ["Cold storage ammonia systems", "Light manufacturing operations", "Geographic spread"],
            "positive_factors": ["Modern construction", "Strong protection systems", "Experienced operators"],
            "loss_history": {"total_claims": 4, "total_paid": 687500, "open_claims": 1}
        },
        "CRE-2026-003-HRT": {
            "name": "Coastal Hospitality Holdings - Hotels & Retail",
            "property_type": "Hospitality & Retail",
            "location": "Miami, FL",
            "tiv": 505000000,
            "locations": 4,
            "risk_score": 52,
            "risk_tier": "High",
            "premium_estimate": 2150000,
            "decision": "Refer to Underwriting Manager",
            "key_concerns": ["Hurricane exposure", "Significant loss history", "Coastal flood zone", "Open claim pending"],
            "positive_factors": ["Hurricane-rated construction", "Recent $85M renovation", "Strong occupancy rates"],
            "loss_history": {"total_claims": 5, "total_paid": 7350000, "open_claims": 1, "hurricane_losses": 7050000}
        }
    }

    # Risk scoring factors
    RISK_FACTORS = {
        "construction": {"fire_resistive": 95, "masonry": 85, "frame": 70, "wood": 60},
        "protection_class": {1: 98, 2: 95, 3: 90, 4: 85, 5: 80, 6: 75, 7: 70, 8: 65, 9: 60, 10: 50},
        "sprinklered": {"full": 15, "partial": 8, "none": 0},
        "age_deduction": {"new": 0, "10_years": -3, "25_years": -8, "50_years": -15}
    }

    @classmethod
    def get_deal_by_id(cls, deal_id: str) -> Optional[Dict]:
        """Get deal information by submission ID."""
        return cls.PROCESSED_DEALS.get(deal_id.upper())

    @classmethod
    def search_deals(cls, query: str) -> List[Dict]:
        """Search deals by name, location, or property type."""
        query_lower = query.lower()
        matches = []
        for deal_id, deal in cls.PROCESSED_DEALS.items():
            if (query_lower in deal["name"].lower() or
                query_lower in deal["location"].lower() or
                query_lower in deal["property_type"].lower()):
                matches.append({**deal, "submission_id": deal_id})
        return matches


class CREUnderwritingBot:
    """Intelligent CRE Underwriting Assistant for demo with conversation context."""

    # Class-level context to persist across requests
    _conversation_state = {
        "last_deal_id": None,
        "last_topic": None,  # 'risk', 'premium', 'loss', 'decision', 'overview'
        "last_response_offered": [],  # What options we offered
    }

    def __init__(self):
        self.kb = CREUnderwritingKnowledgeBase()

    def _update_context(self, deal_id: str = None, topic: str = None, offered: List[str] = None):
        """Update conversation context."""
        if deal_id:
            self._conversation_state["last_deal_id"] = deal_id
        if topic:
            self._conversation_state["last_topic"] = topic
        if offered:
            self._conversation_state["last_response_offered"] = offered

    def _is_follow_up(self, prompt: str) -> bool:
        """Check if this is a follow-up response."""
        follow_up_phrases = [
            "yes", "yeah", "yep", "sure", "ok", "okay", "please", "tell me more",
            "go ahead", "continue", "more details", "more info", "explain",
            "show me", "what about", "how about", "and the", "what's the",
            "yes please", "sounds good", "let's see", "give me", "i want to know",
            "tell me about", "elaborate", "details", "break it down", "dive deeper"
        ]
        prompt_lower = prompt.lower().strip()
        return any(phrase in prompt_lower for phrase in follow_up_phrases) and len(prompt_lower) < 50

    def _handle_follow_up(self, prompt: str) -> Optional[str]:
        """Handle follow-up questions based on conversation context."""
        prompt_lower = prompt.lower()
        last_deal = self._conversation_state.get("last_deal_id")
        last_topic = self._conversation_state.get("last_topic")
        offered = self._conversation_state.get("last_response_offered", [])

        if not last_deal:
            return None

        # Check if user is asking for specific offered topics
        if any(word in prompt_lower for word in ["risk", "score", "assessment"]) or "risk" in offered and self._is_simple_yes(prompt_lower):
            return self._handle_deal_query(last_deal, "risk score")

        if any(word in prompt_lower for word in ["premium", "price", "quote", "cost"]) or "premium" in offered and self._is_simple_yes(prompt_lower):
            return self._handle_deal_query(last_deal, "premium estimate")

        if any(word in prompt_lower for word in ["loss", "claim", "history"]) or "loss" in offered and self._is_simple_yes(prompt_lower):
            return self._handle_deal_query(last_deal, "loss history")

        if any(word in prompt_lower for word in ["decision", "recommend", "approve"]):
            return self._handle_deal_query(last_deal, "decision recommendation")

        if any(word in prompt_lower for word in ["concern", "issue", "problem", "red flag"]):
            return self._handle_deal_query(last_deal, "concerns")

        # Simple "yes" - provide all details we offered
        if self._is_simple_yes(prompt_lower) and offered:
            return self._provide_full_details(last_deal)

        # "Tell me more" or "more details" - expand on last topic or provide everything
        if any(phrase in prompt_lower for phrase in ["more", "details", "elaborate", "explain"]):
            return self._provide_full_details(last_deal)

        return None

    def _is_simple_yes(self, prompt: str) -> bool:
        """Check if this is a simple affirmative response."""
        simple_yes = ["yes", "yeah", "yep", "sure", "ok", "okay", "please", "yes please", "yea", "y"]
        return prompt.strip().lower().rstrip('.!') in simple_yes

    def _provide_full_details(self, deal_id: str) -> str:
        """Provide comprehensive details for a deal."""
        deal = self.kb.PROCESSED_DEALS.get(deal_id)
        if not deal:
            return "I couldn't find that deal. Which submission would you like to review?"

        lh = deal['loss_history']
        self._update_context(deal_id=deal_id, topic="full_details", offered=[])

        return f"""**Complete Analysis: {deal['name']}**
**Submission ID:** {deal_id}

---

## Risk Assessment

**Risk Score:** {deal['risk_score']}/100
**Risk Tier:** {deal['risk_tier']}

**Key Concerns:**
{chr(10).join(f'- {c}' for c in deal['key_concerns'])}

**Positive Factors:**
{chr(10).join(f'- {p}' for p in deal['positive_factors'])}

---

## Premium Analysis

**Total Insured Value:** ${deal['tiv']:,}
**Estimated Annual Premium:** ${deal['premium_estimate']:,}
**Effective Rate:** ${deal['premium_estimate']/deal['tiv']*100:.3f} per $100 TIV

---

## Loss History (5 Years)

| Metric | Value |
|--------|-------|
| Total Claims | {lh['total_claims']} |
| Total Paid | ${lh['total_paid']:,} |
| Open Claims | {lh['open_claims']} |
{f"| Hurricane Losses | ${lh.get('hurricane_losses', 0):,} |" if lh.get('hurricane_losses') else ""}

**Loss Ratio:** {(lh['total_paid'] / deal['premium_estimate'] * 100):.1f}%

---

## Underwriting Decision

**Recommendation:** {deal['decision']}

**Reasoning:**
The combination of {'elevated' if deal['risk_score'] < 65 else 'moderate'} risk score ({deal['risk_score']}) and {'significant' if lh['total_paid'] > 1000000 else 'manageable'} loss history requires {'manager' if 'Manager' in deal['decision'] else 'senior underwriter'} review.

**Required Conditions:**
- {'Wind engineering report required' if 'hurricane' in str(deal['key_concerns']).lower() else 'Standard loss control inspection'}
- {'Close open claims before binding' if lh['open_claims'] > 0 else 'Verify current coverage forms'}
- Annual property inspections recommended

---

**What would you like to explore next?** I can compare this to other submissions, discuss specific concerns in more detail, or provide my recommendation on next steps."""

    def generate_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate an intelligent response based on the prompt with conversation context."""
        prompt_lower = prompt.lower()

        # First, check if this is a follow-up to previous conversation
        if self._is_follow_up(prompt):
            follow_up_response = self._handle_follow_up(prompt)
            if follow_up_response:
                return follow_up_response

        # Check for specific deal queries
        deal_id_match = re.search(r'cre-\d{4}-\d{3}[a-z]*', prompt_lower, re.IGNORECASE)
        if deal_id_match:
            return self._handle_deal_query(deal_id_match.group().upper(), prompt_lower)

        # Check for property/location queries
        if any(word in prompt_lower for word in ["chicago", "lakefront", "mixed-use", "mixed use"]):
            return self._handle_deal_query("CRE-2026-001-MUP", prompt_lower)
        if any(word in prompt_lower for word in ["industrial", "warehouse", "midwest", "cold storage"]):
            return self._handle_deal_query("CRE-2026-002-IND", prompt_lower)
        if any(word in prompt_lower for word in ["miami", "hotel", "hospitality", "coastal", "hurricane"]):
            return self._handle_deal_query("CRE-2026-003-HRT", prompt_lower)

        # Handle different query types
        if any(word in prompt_lower for word in ["risk score", "risk rating", "how risky"]):
            return self._handle_risk_query(prompt_lower)

        if any(word in prompt_lower for word in ["premium", "price", "quote", "cost"]):
            return self._handle_premium_query(prompt_lower)

        if any(word in prompt_lower for word in ["loss", "claim", "history"]):
            return self._handle_loss_query(prompt_lower)

        if any(word in prompt_lower for word in ["approve", "decision", "recommend", "decline"]):
            return self._handle_decision_query(prompt_lower)

        if any(word in prompt_lower for word in ["concern", "issue", "problem", "worry", "red flag"]):
            return self._handle_concerns_query(prompt_lower)

        if any(word in prompt_lower for word in ["compare", "versus", "vs", "difference"]):
            return self._handle_comparison_query(prompt_lower)

        if any(word in prompt_lower for word in ["summary", "overview", "status", "queue", "pending"]):
            return self._handle_summary_query(prompt_lower)

        if any(word in prompt_lower for word in ["help", "can you", "what can"]):
            return self._get_help_response()

        if any(word in prompt_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return self._get_greeting_response()

        # Check if there's context from a previous deal we can use
        if self._conversation_state.get("last_deal_id"):
            # Try to interpret the question in context of the last deal
            return self._handle_contextual_query(prompt, self._conversation_state["last_deal_id"])

        # Default response
        return self._get_default_response(prompt)

    def _handle_contextual_query(self, prompt: str, deal_id: str) -> str:
        """Handle queries in context of the current deal."""
        prompt_lower = prompt.lower()
        deal = self.kb.PROCESSED_DEALS.get(deal_id)

        if not deal:
            return self._get_default_response(prompt)

        # Try to match partial queries
        if any(word in prompt_lower for word in ["next", "what else", "anything else", "other"]):
            return f"""For **{deal['name']}**, here are other areas we can explore:

1. **Detailed Risk Breakdown** - Construction, protection, location factors
2. **Premium Components** - How we arrived at ${deal['premium_estimate']:,}
3. **Loss Trend Analysis** - Year-over-year claims patterns
4. **Comparable Accounts** - How this compares to similar risks
5. **Underwriting Conditions** - What we'd require to bind

Which would you like to dive into?"""

        if any(word in prompt_lower for word in ["why", "reason", "explain", "how come"]):
            if deal['risk_score'] < 65:
                return f"""**Why {deal['name']} is rated as {deal['risk_tier']} Risk:**

The risk score of {deal['risk_score']}/100 reflects several factors:

**Negative Impacts (-{100 - deal['risk_score']} points):**
{chr(10).join(f'- {c}' for c in deal['key_concerns'])}

**Mitigating Factors:**
{chr(10).join(f'- {p}' for p in deal['positive_factors'])}

The {'hurricane exposure and loss history' if 'hurricane' in str(deal['key_concerns']).lower() else 'occupancy hazards and complexity'} are the primary drivers of the elevated risk rating.

Would you like me to explain any specific factor in more detail?"""
            else:
                return f"""**Risk Rating Explanation for {deal['name']}:**

The risk score of {deal['risk_score']}/100 reflects a {deal['risk_tier'].lower()} risk profile:

**Strengths:**
{chr(10).join(f'- {p}' for p in deal['positive_factors'])}

**Areas of Concern:**
{chr(10).join(f'- {c}' for c in deal['key_concerns'])}

Overall, the positive factors balance the concerns, resulting in a {deal['risk_tier'].lower()} tier classification."""

        # If we can't figure it out, prompt for clarification while staying in context
        return f"""I'm still focused on **{deal['name']}** ({deal_id}).

Could you clarify what you'd like to know? For example:
- "What's driving the risk score?"
- "Break down the premium"
- "Show me the claims detail"
- "What's your recommendation?"

Or ask me about a different submission if you'd like to switch."""

    def _handle_deal_query(self, deal_id: str, prompt: str) -> str:
        """Handle queries about a specific deal."""
        deal = self.kb.PROCESSED_DEALS.get(deal_id)
        if not deal:
            return f"I couldn't find submission {deal_id}. Available submissions are: CRE-2026-001-MUP (Chicago Mixed-Use), CRE-2026-002-IND (Industrial Portfolio), CRE-2026-003-HRT (Miami Hotels)."

        # Update context - we're now discussing this deal
        self._update_context(deal_id=deal_id)

        if "risk" in prompt:
            self._update_context(deal_id=deal_id, topic="risk", offered=["premium", "loss", "decision"])
            return f"""**Risk Assessment for {deal['name']}** (Submission: {deal_id})

**Risk Score:** {deal['risk_score']}/100
**Risk Tier:** {deal['risk_tier']}

**Key Risk Factors:**
{chr(10).join(f'- {c}' for c in deal['key_concerns'])}

**Positive Factors:**
{chr(10).join(f'- {p}' for p in deal['positive_factors'])}

**Analysis:**
The risk score of {deal['risk_score']} places this in our {deal['risk_tier']} tier. {'This requires senior review due to the complexity.' if deal['risk_score'] < 75 else 'Standard underwriting guidelines apply.'}

{'The primary driver is ' + deal['key_concerns'][0].lower() + ', which accounts for approximately ' + str(random.randint(15, 25)) + ' points of deduction.' if deal['key_concerns'] else ''}

Would you like to see the **premium calculation** or **loss history** for this account?"""

        if any(word in prompt for word in ["premium", "price", "quote"]):
            self._update_context(deal_id=deal_id, topic="premium", offered=["risk", "loss", "decision"])
            base_rate = deal['premium_estimate'] / deal['tiv'] * 100
            return f"""**Premium Analysis for {deal['name']}**

**Summary:**
| Metric | Value |
|--------|-------|
| Total Insured Value | ${deal['tiv']:,} |
| Annual Premium | ${deal['premium_estimate']:,} |
| Effective Rate | ${base_rate:.3f} per $100 |

**Premium Build-Up:**
- Base Rate: ${base_rate * 0.7:.3f}
- Occupancy Adjustment: +${base_rate * 0.15:.3f} ({deal['property_type']})
- Loss Experience: +${base_rate * 0.1:.3f}
- Protection Credits: -${base_rate * 0.05:.3f}
- **Final Rate:** ${base_rate:.3f}

**Key Factors:**
- {deal['property_type']} occupancy class
- {deal['locations']} location{'s' if deal['locations'] > 1 else ''}
- Risk score of {deal['risk_score']} impacts experience rating

{'Note: This account has CAT loading of approximately 40% due to hurricane exposure.' if 'hurricane' in str(deal['key_concerns']).lower() else ''}

Shall I show you the **loss history** that's driving the experience rating, or the **risk assessment** breakdown?"""

        if any(word in prompt for word in ["loss", "claim", "history"]):
            lh = deal['loss_history']
            self._update_context(deal_id=deal_id, topic="loss", offered=["risk", "premium", "decision"])
            loss_ratio = (lh['total_paid'] / deal['premium_estimate']) * 100

            return f"""**Loss History Analysis for {deal['name']}**

**5-Year Summary:**
| Metric | Value | Assessment |
|--------|-------|------------|
| Total Claims | {lh['total_claims']} | {'High' if lh['total_claims'] >= 4 else 'Acceptable'} |
| Total Paid | ${lh['total_paid']:,} | {'Concerning' if lh['total_paid'] > 1000000 else 'Normal'} |
| Open Claims | {lh['open_claims']} | {'Action Required' if lh['open_claims'] > 0 else 'Clear'} |
| Loss Ratio | {loss_ratio:.1f}% | {'Elevated' if loss_ratio > 25 else 'Acceptable'} |
{f"| Hurricane Losses | ${lh.get('hurricane_losses', 0):,} | Major Driver |" if lh.get('hurricane_losses') else ""}

**Trend Analysis:**
{'This account shows a concerning pattern of catastrophe losses. The hurricane exposure is a significant underwriting consideration.' if lh.get('hurricane_losses') else 'Claims are spread across typical property perils with no concerning patterns.'}

**Underwriting Impact:**
{'- Loss frequency is elevated - requires discussion with account' if lh['total_claims'] >= 4 else '- Loss frequency is within acceptable parameters'}
{'- **CRITICAL:** Open claims must be resolved or adequately reserved before binding' if lh['open_claims'] > 0 else '- No open claims - clear to proceed'}
- Experience modification will impact renewal pricing

Would you like my **underwriting recommendation** for this account, or should we look at the **risk factors** in more detail?"""

        if any(word in prompt for word in ["decision", "recommend", "approve"]):
            self._update_context(deal_id=deal_id, topic="decision", offered=["risk", "premium", "loss"])
            lh = deal['loss_history']

            # Determine approval likelihood
            if deal['risk_score'] >= 70 and lh['open_claims'] == 0:
                likelihood = "**Likely Approved** with standard conditions"
                color = "good"
            elif deal['risk_score'] >= 55:
                likelihood = "**Conditional Approval** possible with additional requirements"
                color = "moderate"
            else:
                likelihood = "**Challenging** - significant conditions required or potential decline"
                color = "concerning"

            return f"""**Underwriting Decision Analysis: {deal['name']}**

## My Recommendation: {deal['decision']}

**Approval Likelihood:** {likelihood}

---

### Decision Factors

| Factor | Value | Impact |
|--------|-------|--------|
| Risk Score | {deal['risk_score']}/100 | {'Favorable' if deal['risk_score'] >= 70 else 'Concerning' if deal['risk_score'] < 60 else 'Moderate'} |
| Loss Ratio | {(lh['total_paid'] / deal['premium_estimate'] * 100):.1f}% | {'Unfavorable' if lh['total_paid'] > deal['premium_estimate'] * 0.25 else 'Acceptable'} |
| Open Claims | {lh['open_claims']} | {'Blocker' if lh['open_claims'] > 0 else 'Clear'} |
| TIV | ${deal['tiv']:,} | {'Requires Manager' if deal['tiv'] > 250000000 else 'Within Authority'} |

---

### Required Conditions

{'**Must Have:**' if lh['open_claims'] > 0 or deal['risk_score'] < 60 else '**Recommended:**'}
- {'**Close or reserve open claims before binding**' if lh['open_claims'] > 0 else 'Standard loss control inspection'}
- {'Wind engineering report required' if 'hurricane' in str(deal['key_concerns']).lower() else 'Property condition verification'}
- {'Minimum 5% named storm deductible' if 'hurricane' in str(deal['key_concerns']).lower() else 'Review coverage forms for adequacy'}

---

### Next Steps

1. **Route to:** {'Underwriting Manager' if 'Manager' in deal['decision'] else 'Senior Underwriter'}
2. **Information Needed:** {'Wind/flood engineering reports, updated loss runs' if 'hurricane' in str(deal['key_concerns']).lower() else 'Current loss runs, property updates'}
3. **Target Turnaround:** 48-72 hours

---

Would you like me to **prepare a referral summary** for the {'manager' if 'Manager' in deal['decision'] else 'senior underwriter'}, or compare this to our **other submissions** in the queue?"""

        # General deal summary - update context with what we're offering
        self._update_context(deal_id=deal_id, topic="overview", offered=["risk", "premium", "loss"])

        return f"""**Submission Summary: {deal['name']}**
**ID:** {deal_id}

**Property Information:**
- Type: {deal['property_type']}
- Location: {deal['location']}
- Total Insured Value: ${deal['tiv']:,}
- Number of Locations: {deal['locations']}

**Underwriting Assessment:**
- Risk Score: {deal['risk_score']}/100 ({deal['risk_tier']})
- Premium Estimate: ${deal['premium_estimate']:,}
- Decision: {deal['decision']}

**Key Concerns:**
{chr(10).join(f'- {c}' for c in deal['key_concerns'])}

Would you like more details on the **risk assessment**, **premium calculation**, or **loss history**? Just say "yes" or pick one."""

    def _handle_risk_query(self, prompt: str) -> str:
        """Handle general risk-related queries."""
        return """**Risk Scoring Methodology**

Our CRE risk score (0-100) considers:

**Construction (25% weight)**
- Fire Resistive: 95 points
- Masonry Non-Combustible: 85 points
- Frame: 70 points

**Protection Class (20% weight)**
- Class 1-2: Excellent (95+ points)
- Class 3-5: Good (80-90 points)
- Class 6+: Below average (<75 points)

**Loss History (25% weight)**
- 5-year claims frequency and severity
- Loss ratio vs. premium
- Claim types and trends

**Occupancy (15% weight)**
- Hazard grade of operations
- Tenant quality and stability

**Building Age & Condition (15% weight)**
- Year built and renovations
- Maintenance quality
- Code compliance

**Risk Tiers:**
- 80-100: Preferred (Auto-approve eligible)
- 65-79: Acceptable (Standard review)
- 50-64: Moderate (Senior UW review)
- Below 50: High (Manager review or decline)

Which submission would you like me to analyze?"""

    def _handle_premium_query(self, prompt: str) -> str:
        """Handle premium-related queries."""
        return """**Premium Calculation Overview**

Our CRE premiums are calculated using:

**Base Rate Factors:**
- Property type and construction
- Location/territory
- Protection class
- Building age

**Modifications:**
- Experience rating based on loss history
- Schedule rating for unique features
- Protective safeguards credits
- Sprinkler discounts (up to 15%)

**Current Portfolio Summary:**
| Submission | TIV | Premium | Rate |
|------------|-----|---------|------|
| CRE-2026-001-MUP | $226M | $645K | $0.285 |
| CRE-2026-002-IND | $372M | $892K | $0.240 |
| CRE-2026-003-HRT | $505M | $2.15M | $0.426 |

The Miami hospitality account shows higher rates due to hurricane exposure and elevated loss experience.

Would you like a detailed breakdown for a specific submission?"""

    def _handle_loss_query(self, prompt: str) -> str:
        """Handle loss history queries."""
        return """**Loss History Analysis - Current Queue**

**CRE-2026-001-MUP (Chicago Mixed-Use)**
- Claims: 2 | Paid: $312,500 | Open: 0
- Loss Ratio: 12% - *Favorable*

**CRE-2026-002-IND (Industrial Portfolio)**
- Claims: 4 | Paid: $687,500 | Open: 1
- Loss Ratio: 19% - *Acceptable*
- Note: Equipment breakdown claim pending

**CRE-2026-003-HRT (Miami Hotels)**
- Claims: 5 | Paid: $7,350,000 | Open: 1
- Loss Ratio: 35% - *Elevated*
- Note: $7M+ in hurricane losses, open Milton claim

**Red Flags Identified:**
1. Miami portfolio has significant CAT exposure
2. Open claims should be resolved before binding
3. Equipment breakdown coverage recommended for industrial

Would you like me to dive deeper into any specific account's loss history?"""

    def _handle_decision_query(self, prompt: str) -> str:
        """Handle decision-related queries."""
        return """**Pending Underwriting Decisions**

**Auto-Approve Eligible:** None currently
(Requires risk score 80+ with no open claims)

**Standard Review:**
None in queue

**Senior Underwriter Review:**
1. **CRE-2026-001-MUP** - Risk Score 72
   - Mixed-use complexity requires senior expertise

2. **CRE-2026-002-IND** - Risk Score 68
   - Cold storage and manufacturing operations

**Manager Review Required:**
3. **CRE-2026-003-HRT** - Risk Score 52
   - TIV exceeds $500M threshold
   - Hurricane loss history >$5M
   - Open claim pending

**Recommended Actions:**
1. Expedite review of Chicago and Industrial accounts
2. Request wind engineering report for Miami
3. Schedule loss control inspections for all three

Shall I prepare the referral packages?"""

    def _handle_concerns_query(self, prompt: str) -> str:
        """Handle queries about concerns or red flags."""
        return """**Risk Concerns Across Current Queue**

**High Priority (Immediate Attention):**
- Miami Hotels: Hurricane Milton claim still open ($850K reserved)
- Miami Hotels: Coastal flood zone exposure (Zone AE)
- Industrial: Ammonia refrigeration systems at cold storage facility

**Medium Priority (Review Required):**
- Chicago: Recent $187K water damage claim (2023)
- Industrial: Light manufacturing operations increase hazard
- Industrial: Geographic spread across 5 states

**Standard Monitoring:**
- Chicago: 35-story high-rise complexity
- Industrial: High automation equipment values
- All: Ensure adequate business income coverage

**Mitigation Recommendations:**
1. Require hurricane preparedness plan for Miami
2. Verify ammonia system maintenance records
3. Confirm sprinkler inspection dates
4. Review building ordinance coverage adequacy

Would you like detailed mitigation strategies for any specific concern?"""

    def _handle_comparison_query(self, prompt: str) -> str:
        """Handle comparison queries between deals."""
        return """**Portfolio Comparison Analysis**

| Metric | Chicago Mixed-Use | Industrial | Miami Hotels |
|--------|------------------|------------|--------------|
| **TIV** | $226M | $372M | $505M |
| **Locations** | 3 | 5 | 4 |
| **Risk Score** | 72 | 68 | 52 |
| **Risk Tier** | Moderate | Acceptable | High |
| **Premium Est.** | $645K | $892K | $2.15M |
| **Rate per $100** | $0.285 | $0.240 | $0.426 |
| **5-Yr Losses** | $312K | $687K | $7.35M |
| **Loss Ratio** | 12% | 19% | 35% |

**Key Observations:**
1. **Best Risk Profile:** Chicago Mixed-Use - lowest loss ratio, modern construction
2. **Best Rate:** Industrial - efficient operations, spread of risk
3. **Highest Concern:** Miami Hotels - CAT exposure driving poor loss experience

**Recommended Priority:**
1. Industrial - Acceptable with conditions
2. Chicago - Standard review, likely approve
3. Miami - Requires significant conditions or decline consideration

Need more detailed comparison on any specific metric?"""

    def _handle_summary_query(self, prompt: str) -> str:
        """Handle summary/status queries."""
        return """**CRE Underwriting Queue Summary**

**Current Status:**
- Total Submissions: 3
- Combined TIV: $1.1 Billion
- Estimated Premium Pool: $3.69M

**Queue Breakdown:**
| Status | Count | TIV |
|--------|-------|-----|
| Pending Review | 3 | $1.1B |
| Processing | 0 | - |
| Completed | 0 | - |

**Submissions in Queue:**
1. **CRE-2026-001-MUP** - Chicago Mixed-Use | $226M | Score: 72
2. **CRE-2026-002-IND** - Industrial Portfolio | $372M | Score: 68
3. **CRE-2026-003-HRT** - Miami Hotels | $505M | Score: 52

**Action Items:**
- 2 submissions ready for Senior UW review
- 1 submission requires Manager review
- 0 submissions eligible for auto-approval

**Today's Priority:**
Start with Industrial Portfolio - cleanest risk profile and straightforward underwriting.

What would you like to review first?"""

    def _get_help_response(self) -> str:
        """Return help information."""
        return """**CRE Underwriting Assistant - Help**

I can help you with:

**Deal Analysis:**
- "Tell me about CRE-2026-001-MUP"
- "What's the risk score for the Miami hotels?"
- "Show me the loss history for the industrial portfolio"

**Risk Assessment:**
- "What are the concerns for the Chicago property?"
- "Why is the Miami account high risk?"
- "Explain the risk scoring methodology"

**Premium & Pricing:**
- "What's the premium estimate for the hospitality account?"
- "Compare rates across all submissions"
- "Why is Miami priced higher?"

**Decisions & Workflow:**
- "What's your recommendation on CRE-2026-002?"
- "Which deals need manager review?"
- "What's pending in the queue?"

**Comparisons:**
- "Compare Chicago vs Miami deals"
- "Which submission has the best risk profile?"

Just ask naturally - I understand context and can follow up on previous questions!"""

    def _get_greeting_response(self) -> str:
        """Return greeting response."""
        greetings = [
            "Hello! I'm your CRE Underwriting Assistant. I have 3 submissions in the queue ready for review - a Chicago mixed-use portfolio, a Midwest industrial portfolio, and Miami hotels. What would you like to analyze?",
            "Good day! I'm here to help with your commercial real estate underwriting. We have $1.1B in TIV across 3 submissions pending review. Where would you like to start?",
            "Hi there! Ready to help with CRE underwriting. I can provide risk assessments, premium calculations, loss history analysis, and decision recommendations. What can I help you with?"
        ]
        return random.choice(greetings)

    def _get_default_response(self, prompt: str) -> str:
        """Return default response for unrecognized queries."""
        return f"""I understand you're asking about "{prompt[:50]}{'...' if len(prompt) > 50 else ''}".

I'm specialized in CRE underwriting and can help with:
- **Risk Analysis:** Risk scores, concerns, positive factors
- **Premium Calculation:** Rates, pricing factors, comparisons
- **Loss History:** Claims data, trends, red flags
- **Decisions:** Recommendations, approvals, referrals

**Current Submissions Available:**
- CRE-2026-001-MUP (Chicago Mixed-Use, $226M)
- CRE-2026-002-IND (Industrial Portfolio, $372M)
- CRE-2026-003-HRT (Miami Hotels, $505M)

Could you rephrase your question or ask about one of these deals?"""


class AerospaceDefenseBot:
    """Intelligent Aerospace & Defense Assistant for demo conversations."""

    # Sample contracts and work orders
    CONTRACTS = {
        "FA8501-24-C-0012": {
            "name": "F-35 Titanium Housing Assembly",
            "program": "F-35 Lightning II",
            "prime": "Lockheed Martin",
            "value": 4250000,
            "type": "FFP",
            "clins": 3,
            "status": "Active",
            "delivery_date": "2026-09-15",
            "dfars_clauses": ["252.204-7012", "252.225-7001", "252.227-7013"],
            "itar_controlled": True
        },
        "W58RGZ-25-C-0089": {
            "name": "Apache Helicopter Gearbox Components",
            "program": "AH-64E Apache",
            "prime": "Boeing Defense",
            "value": 2875000,
            "type": "CPFF",
            "clins": 5,
            "status": "Active",
            "delivery_date": "2026-12-01",
            "dfars_clauses": ["252.204-7012", "252.211-7003", "252.246-7007"],
            "itar_controlled": True
        },
        "N00019-24-C-1156": {
            "name": "F/A-18 Fuel System Brackets",
            "program": "F/A-18 Super Hornet",
            "prime": "Boeing Defense",
            "value": 1650000,
            "type": "FFP",
            "clins": 2,
            "status": "Pending Award",
            "delivery_date": "2026-06-30",
            "dfars_clauses": ["252.204-7012", "252.225-7001"],
            "itar_controlled": True
        }
    }

    WORK_ORDERS = {
        "WO-2026-0342": {
            "part_number": "7842-A",
            "description": "Titanium Housing - 5-axis machined",
            "contract": "FA8501-24-C-0012",
            "quantity": 25,
            "status": "In Production",
            "operations": ["CNC Rough", "CNC Finish", "Deburr", "Inspect", "NDT"],
            "current_op": "CNC Finish",
            "due_date": "2026-04-15"
        },
        "WO-2026-0358": {
            "part_number": "9215-C",
            "description": "Aluminum Bracket Assembly",
            "contract": "N00019-24-C-1156",
            "quantity": 100,
            "status": "Queued",
            "operations": ["CNC Mill", "Anodize", "Inspect"],
            "current_op": "Pending",
            "due_date": "2026-05-01"
        }
    }

    PRICING_HISTORY = {
        "titanium_housing": {"avg_price": 12500, "min": 10800, "max": 15200, "margin": 0.22},
        "aluminum_bracket": {"avg_price": 285, "min": 245, "max": 340, "margin": 0.18},
        "gearbox_component": {"avg_price": 8750, "min": 7200, "max": 11000, "margin": 0.25}
    }

    def generate_response(self, prompt: str, agent_type: str = "contract") -> str:
        """Generate aerospace-specific response based on prompt and agent type."""
        prompt_lower = prompt.lower()

        # Handle greetings first
        if any(w in prompt_lower for w in ["hello", "hi", "help", "what can"]):
            return self._get_greeting(agent_type)

        # Route based on agent type
        if agent_type == "pricing" or any(w in prompt_lower for w in ["price", "pricing", "quote", "estimate", "cost"]):
            return self._handle_pricing_query(prompt_lower)
        elif agent_type == "design" or any(w in prompt_lower for w in ["design", "cad", "model", "drawing"]):
            return self._handle_design_query(prompt_lower)
        elif agent_type == "cnc" or any(w in prompt_lower for w in ["cnc", "gcode", "g-code", "machining", "program"]):
            return self._handle_cnc_query(prompt_lower)
        elif agent_type == "workorder" or any(w in prompt_lower for w in ["work order", "workorder", "wo-", "production"]):
            return self._handle_workorder_query(prompt_lower)
        elif agent_type == "contract" or "contract" in prompt_lower:
            return self._handle_contract_query(prompt_lower)
        else:
            return self._handle_general_query(prompt_lower, agent_type)

    def _handle_contract_query(self, prompt: str) -> str:
        """Handle contract-related queries."""
        # Check for specific contract
        for contract_id, contract in self.CONTRACTS.items():
            if contract_id.lower() in prompt or contract["program"].lower() in prompt:
                return f"""**Contract Details: {contract_id}**

**Program:** {contract['program']}
**Prime Contractor:** {contract['prime']}
**Contract Value:** ${contract['value']:,}
**Type:** {contract['type']}
**Status:** {contract['status']}
**Delivery Date:** {contract['delivery_date']}

**DFARS Clauses:**
{chr(10).join(f'- {clause}' for clause in contract['dfars_clauses'])}

**ITAR Status:** {'Controlled - Export restrictions apply' if contract['itar_controlled'] else 'Not controlled'}

**CLINs:** {contract['clins']} line items

Would you like me to:
- Show pricing history for similar parts?
- Review compliance requirements?
- Check production status?"""

        # General contract query
        return f"""**Active Contracts Summary**

| Contract | Program | Prime | Value | Status |
|----------|---------|-------|-------|--------|
| FA8501-24-C-0012 | F-35 Lightning II | Lockheed Martin | $4.25M | Active |
| W58RGZ-25-C-0089 | AH-64E Apache | Boeing Defense | $2.88M | Active |
| N00019-24-C-1156 | F/A-18 Super Hornet | Boeing Defense | $1.65M | Pending |

**Total Contract Value:** $8.78M
**Active Programs:** 3

**Compliance Status:**
- All contracts require DFARS 252.204-7012 (Cybersecurity)
- ITAR export controls in effect
- AS9100D certification current

What contract would you like to review in detail?"""

    def _handle_cnc_query(self, prompt: str) -> str:
        """Handle CNC programming queries."""
        if any(w in prompt for w in ["review", "check", "analyze", "7842"]):
            return """**CNC Program Review: Part 7842-A (Titanium Housing)**

**Program:** OP20_FINISH_7842A.nc
**Machine:** DMG MORI DMU 80P (5-axis)
**Material:** Ti-6Al-4V (Grade 5 Titanium)

**Analysis Results:**

✅ **Tool Selection:** APPROVED
- T01: 1/2" Carbide End Mill (TiAlN coated) - Correct for titanium
- T02: 3/8" Ball End Mill - Appropriate for contour finishing
- T03: 1/4" Drill - Correct for hole features

⚠️ **Feed Rate Warning:**
- Line 142: F12.0 may be aggressive for Ti-6Al-4V pocket
- Recommendation: Reduce to F8.0 for tool life

✅ **Speeds:** APPROVED
- S2400 RPM appropriate for 1/2" in titanium
- SFM = 314, within recommended range (250-400)

✅ **Coolant:** High-pressure coolant M08 enabled

**Compliance Checks:**
- ✅ Tool life tracking enabled
- ✅ In-process inspection points included
- ✅ First article inspection callout at line 285

**Estimated Cycle Time:** 47 minutes
**Previous Best:** 52 minutes (8.5% improvement)

Would you like me to generate the optimized program or review specific operations?"""

        return """**CNC Programming Assistant**

I can help you with:

**Program Review:**
- G-code analysis and optimization
- Feed/speed recommendations for aerospace materials
- Tool selection verification
- Compliance checks (AS9100, NADCAP)

**Available Programs:**
| Program | Part | Material | Status |
|---------|------|----------|--------|
| OP20_FINISH_7842A.nc | Titanium Housing | Ti-6Al-4V | Ready for review |
| OP10_ROUGH_9215C.nc | Aluminum Bracket | 7075-T6 | In production |

**Quick Commands:**
- "Review CNC program for 7842-A"
- "Optimize feeds for titanium"
- "Check tool life on T01"

What would you like me to analyze?"""

    def _handle_workorder_query(self, prompt: str) -> str:
        """Handle work order queries."""
        for wo_id, wo in self.WORK_ORDERS.items():
            if wo_id.lower() in prompt or wo["part_number"].lower() in prompt:
                ops_status = []
                current_found = False
                for op in wo["operations"]:
                    if op == wo["current_op"]:
                        ops_status.append(f"▶️ **{op}** (In Progress)")
                        current_found = True
                    elif not current_found:
                        ops_status.append(f"✅ {op}")
                    else:
                        ops_status.append(f"⏳ {op}")

                return f"""**Work Order: {wo_id}**

**Part:** {wo['part_number']} - {wo['description']}
**Contract:** {wo['contract']}
**Quantity:** {wo['quantity']} units
**Due Date:** {wo['due_date']}
**Status:** {wo['status']}

**Operations:**
{chr(10).join(ops_status)}

**Current Operation:** {wo['current_op']}
**Progress:** {wo['operations'].index(wo['current_op']) + 1}/{len(wo['operations'])} operations complete

Would you like me to:
- Update operation status?
- Create NCR if needed?
- Check material availability?"""

        return """**Work Order Queue**

| WO Number | Part | Qty | Status | Due Date |
|-----------|------|-----|--------|----------|
| WO-2026-0342 | 7842-A Titanium Housing | 25 | In Production | 2026-04-15 |
| WO-2026-0358 | 9215-C Aluminum Bracket | 100 | Queued | 2026-05-01 |

**Production Summary:**
- In Production: 1
- Queued: 1
- On Hold: 0

**Alerts:**
- ⚠️ WO-2026-0342 requires NDT scheduling
- ℹ️ WO-2026-0358 material staged and ready

Which work order would you like to review?"""

    def _handle_pricing_query(self, prompt: str) -> str:
        """Handle pricing prediction queries."""
        return """**Pricing Analysis & Prediction**

**Historical Pricing Data:**

| Part Type | Avg Price | Range | Target Margin |
|-----------|-----------|-------|---------------|
| Titanium Housing | $12,500 | $10.8K-$15.2K | 22% |
| Aluminum Bracket | $285 | $245-$340 | 18% |
| Gearbox Component | $8,750 | $7.2K-$11K | 25% |

**Current Quote Request:**
For 25x Titanium Housings (Part 7842-A):

| Cost Element | Amount |
|--------------|--------|
| Material (Ti-6Al-4V) | $87,500 |
| Labor (47 hrs × 25) | $94,000 |
| Overhead | $36,300 |
| **Total Cost** | **$217,800** |
| Target Margin (22%) | $47,916 |
| **Recommended Price** | **$265,716** |
| **Per Unit** | **$10,629** |

**Competitive Analysis:**
- Below market avg ($12,500) by 15%
- Within historical range ✅
- Meets margin target ✅

**Recommendation:** Quote at $10,800/unit ($270,000 total) to remain competitive while maintaining margin.

Would you like me to generate a formal quote or analyze different quantities?"""

    def _handle_design_query(self, prompt: str) -> str:
        """Handle design assistant queries."""
        return """**Product Design Assistant - Aerospace**

**Current Design Projects:**

| Project | Part | Status | Rev |
|---------|------|--------|-----|
| F-35 Housing Redesign | 7842-A | In Review | C |
| Apache Bracket Update | 9215-C | Released | B |
| New Gearbox Mount | 1156-D | Concept | A |

**Design Capabilities:**
- **DFM Analysis:** Manufacturability review for machined parts
- **Material Selection:** Aerospace-grade material recommendations
- **Tolerance Analysis:** GD&T verification and optimization
- **Weight Optimization:** Topology optimization for aerospace

**Recent Design Changes:**
- 7842-A Rev C: Reduced wall thickness from 0.125" to 0.100" (15% weight savings)
- 9215-C Rev B: Added fillet radii for improved fatigue life

**Compliance:**
- All designs meet MIL-STD-129 marking requirements
- ITAR data handling protocols in effect

What would you like me to help you with?"""

    def _get_greeting(self, agent_type: str) -> str:
        """Return appropriate greeting based on agent type."""
        greetings = {
            "contract": """**ContractBot - Aerospace & Defense**

Hello! I'm your defense contract specialist. I can help you with:

- **Contract Lookup:** Search historical contracts and pricing
- **RFP Analysis:** Extract requirements and compliance obligations
- **Pricing Prediction:** Generate competitive quotes based on history
- **DFARS/ITAR Compliance:** Check clause requirements

**Active Contracts:** 3 programs worth $8.78M
**Pending RFPs:** 1

What would you like to work on?""",

            "cnc": """**CNCBot - Aerospace Manufacturing**

Hello! I'm your CNC programming assistant. I can help with:

- **G-code Review:** Analyze programs for aerospace materials
- **Feed/Speed Optimization:** Material-specific recommendations
- **Compliance Checks:** AS9100, NADCAP requirements
- **Tool Selection:** Verify tooling for titanium, Inconel, etc.

**Programs Ready for Review:** 2
**Active Machines:** DMG MORI 5-axis, Mazak HCN-5000

What would you like me to analyze?""",

            "workorder": """**WorkOrderBot - Production Management**

Hello! I'm your work order management assistant. I can help with:

- **Work Order Status:** Track production progress
- **ERP Updates:** Read/write to production system
- **NCR Creation:** Document non-conformances
- **Routing Optimization:** Improve operation sequences

**Active Work Orders:** 2
**In Production:** 1
**Due This Week:** 0

Which work order would you like to review?""",

            "pricing": """**PricingBot - Aerospace Pricing & Estimation**

Hello! I'm your pricing prediction assistant. I can help with:

- **Historical Analysis:** Review past quotes and win rates
- **Cost Estimation:** Material, labor, and overhead calculations
- **Competitive Pricing:** Market-based recommendations
- **Margin Optimization:** Target profitability analysis

**Recent Quotes:**
- F-35 Titanium Housing: $10,629/unit (won)
- Apache Gearbox Component: $8,750/unit (pending)
- F/A-18 Bracket: $285/unit (won)

What pricing analysis would you like?""",

            "design": """**DesignBot - Aerospace Product Design**

Hello! I'm your product design assistant. I can help with:

- **DFM Analysis:** Design for manufacturability review
- **Material Selection:** Aerospace-grade recommendations
- **Tolerance Analysis:** GD&T verification
- **Weight Optimization:** Topology optimization

**Active Projects:** 3
**Pending Reviews:** 1

What design task can I help you with?"""
        }
        return greetings.get(agent_type, greetings["contract"])

    def _handle_general_query(self, prompt: str, agent_type: str) -> str:
        """Handle general queries."""
        return f"""I understand you're asking about "{prompt[:50]}{'...' if len(prompt) > 50 else ''}".

As your {agent_type.title()}Bot, I specialize in:

**Contract Analysis:**
- FA8501-24-C-0012 (F-35 Program)
- W58RGZ-25-C-0089 (Apache Program)
- N00019-24-C-1156 (F/A-18 Program)

**Production:**
- WO-2026-0342 (Titanium Housing)
- WO-2026-0358 (Aluminum Bracket)

**Quick Commands:**
- "Show active contracts"
- "Review CNC program for 7842-A"
- "Check work order status"
- "Generate pricing estimate"

How can I help you today?"""


class AgentSimulatorBase:
    """Service for invoking Foundry Agent Service runtime agents."""

    # Deployed agent ARNs
    # Runtime ids are supplied by the concrete runtime subclass.
    AGENT_ARNS: dict = {}

    # EPROD agent keys — hard-route to Foundry Agent Service runtimes (deployed). Keeps
    # them from being grabbed by aerospace/CBB/CRE keyword matchers (e.g.
    # `apex-eprod-quote-bot` could collide with the CRE "quote" sub-string).
    EPROD_AGENT_IDS = {
        "eprod-invoice-agent",  "eprodinvoiceagent",  "apex_eprod_invoice_bot",
        "eprod-po-agent",       "eprodpoagent",       "apex_eprod_po_bot",
        "eprod-vendor-agent",   "eprodvendoragent",   "apex_eprod_vendor_bot",
        "eprod-quote-agent",    "eprodquoteagent",    "apex_eprod_quote_bot",
        "eprod-tariff-agent",   "eprodtariffagent",   "apex_eprod_tariff_bot",
        "eprod-jib-agent",      "eprodjibagent",      "apex_eprod_jib_bot",
    }

    # CWFCU (CommunityWide FCU) agent keys — hard-route to the in-process
    # simulator. Keeps them away from the financial_services InvoiceAgent
    # keyword matcher (which would otherwise grab "policy", "vendor", etc.).
    CWFCU_AGENT_IDS = {
        "cwfcu-onboarding-agent", "cwfcuonboardingagent",
        "cwfcu-compliance-agent", "cwfcucomplianceagent",
        "cwfcu-loan-agent",       "cwfculoanagent",
        "cwfcu-vendor-agent",     "cwfcuvendoragent",
        "cwfcu-policy-agent",     "cwfcupolicyagent",
    }

    # Boler (The Boler Company) agent keys — hard-route to in-process simulator.
    # 5 agents covering benefits allocation across 5 divisions / 847 employees.
    BOLER_AGENT_IDS = {
        "boler-benefits-agent",  "bolerbenefitsagent",
        "boler-exception-agent", "bolerexceptionagent",
        "boler-je-agent",        "bolerjeagent",
        "boler-signal-agent",    "bolersignalagent",
        "boler-audit-agent",     "bolerauditagent",
    }

    # Verizon Far Edge agent keys — in-process simulator fallback so the 4
    # agents work OFFLINE (no Foundry Agent Service round-trip) anchored on the REAL
    # firmware corpus James Patchett shared (synthetic-data/verizon_far_edge/
    # real_test_reports/ · 118 reports · HPE Edgeline + ZT + Dell).
    VERIZON_AGENT_IDS = {
        "certification-agent",   "certificationagent",
        "schemawatch-agent",     "schemawatchagent",
        "upgrade-advisor-agent", "upgradeadvisoragent",
        "mentor-agent",          "mentoragent",
        "verizon-orchestrator-agent", "verizonorchestratoragent",
        "playbook-agent",        "playbookagent",
    }

    # CBB demo agent keys — must route to their own Foundry Agent Service runtime, NOT the
    # CRE fallback or aerospace bot (the existing keyword matchers can
    # accidentally grab "logistics" or "contract" sub-strings).
    CBB_AGENT_IDS = {
        "customerops-bot", "customerops",
        "qc-bot", "qcbot",
        "logistics-bot", "logisticsbot",
    }

    # STP Phase 2 agent keys — must route to in-process embedded demo data
    # (or to Foundry Agent Service runtimes once deploy_stp_agents.py has run). Like the
    # CBB matcher, this skips keyword routing that could otherwise grab
    # "policy" or "maintenance" sub-strings and route them to the wrong agent.
    STP_AGENT_IDS = {
        "chatstp", "chatstp-router",
        "policy-agent", "policyagent",
        "maintenance-agent", "maintenanceagent",
        "diagnostics-agent", "diagnosticsagent",
        "reliability-agent", "reliabilityagent",
    }

    # Agentic Enterprise (66 Degrees vendor-neutral demo) agent keys.
    # Routed to the in-process simulator in services/agentic_enterprise_demo.py.
    # No Foundry Agent Service deploy required — the demo runs offline.
    AGENTIC_ENTERPRISE_AGENT_IDS = {
        # UC-1: supply chain orchestrator
        "orchestrator-agent", "orchestratoragent", "orchestrator", "supply-orchestrator",
        # UC-2: cruise concierge
        "concierge-agent", "conciergeagent", "concierge", "cruise-concierge",
        # UC-3: lease extraction
        "lease-agent", "leaseagent", "lease",
    }

    # Agents that use local demo mode (intelligent responses without AWS)
    DEMO_AGENTS = {"underwrite-bot", "cre-underwrite-bot", "creunderwritebot"}

    # Aerospace agent keywords for routing
    AEROSPACE_KEYWORDS = {
        "contract": ["contract", "pricing", "rfp", "dfars", "itar", "quote", "bid"],
        "cnc": ["cnc", "gcode", "g-code", "machining", "program", "feed", "speed", "tool"],
        "workorder": ["workorder", "work order", "wo-", "production", "ncr", "operation"]
    }

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.cre_bot = CREUnderwritingBot()
        self.aerospace_bot = AerospaceDefenseBot()

    def _is_cre_underwriting_agent(self, agent_id: str) -> bool:
        """Check if the agent is a CRE underwriting agent (uses demo mode)."""
        agent_id_lower = agent_id.lower().replace("-", "").replace("_", "")
        cre_keywords = ["underwrite", "cre", "insurance", "risk"]
        return any(kw in agent_id_lower for kw in cre_keywords)

    def _is_aerospace_agent(self, agent_id: str) -> bool:
        """Check if the agent is an aerospace/defense agent."""
        agent_id_lower = agent_id.lower().replace("-", "").replace("_", "")
        aerospace_keywords = ["contract", "cnc", "workorder", "aerospace", "defense", "pricing", "prediction", "design", "assistant"]
        return any(kw in agent_id_lower for kw in aerospace_keywords)

    def _get_aerospace_agent_type(self, agent_id: str) -> str:
        """Determine the type of aerospace agent."""
        agent_id_lower = agent_id.lower()
        if "cnc" in agent_id_lower or "programming" in agent_id_lower:
            return "cnc"
        elif "workorder" in agent_id_lower or "work_order" in agent_id_lower:
            return "workorder"
        elif "pricing" in agent_id_lower or "prediction" in agent_id_lower:
            return "pricing"
        elif "design" in agent_id_lower or "assistant" in agent_id_lower:
            return "design"
        else:
            return "contract"

    async def invoke_agent(
        self,
        agent_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        model_overrides: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke an Foundry Agent Service agent with a prompt.

        Routing priority:
          1. CBB agents (customerops, qcbot, logisticsbot) — always go to their
             own deployed Foundry Agent Service runtimes. Skip the aerospace keyword matcher
             (would otherwise grab "logistics") and skip the CRE fallback.
          2. Aerospace agents — match by keyword, use aerospace demo bot.
          3. CRE underwriting — match by keyword, use CRE demo bot.
          4. Everything else with a registered ARN — invoke via AWS CLI.
          5. Truly unknown ids — return a clean error (no CRE lorem).

        Args:
            agent_id: The agent identifier (e.g., 'customerops', 'qcbot').
            prompt:   The user's new message.
            session_id: APEX chat session id. Forwarded to Foundry Agent Service as the
                `runtime-session-id` so the runtime's own server-side memory
                kicks in across turns.
            history: Ordered list of {role, content} dicts for prior turns.
                Prepended to the prompt so the agent can reason over context
                even when its runtime doesn't persist session state.

        Returns:
            Dict with {'success', 'response', 'reasoning', 'actions_taken'}.
        """
        # Build a conversation-aware prompt. Strands agents read
        # payload["prompt"] as a flat string — rather than changing every
        # agent.py entrypoint, we fold the prior turns into the prompt text
        # so Claude has the full context in-window. Server-side memory via
        # runtime-session-id is ALSO passed through for Foundry Agent Service-native
        # state, so we get belt-and-suspenders continuity.
        multi_turn_prompt = self._build_multi_turn_prompt(prompt, history)

        # Normalize agent_id to a canonical form so callers can pass either
        # the display name ("PolicyAgent", "OrchestratorAgent") or the slug
        # ("policy-agent") without affecting routing. We compare against the
        # AGENT_IDS sets in BOTH forms so existing entries (which use mixed
        # conventions) keep working.
        agent_id_norm_slug = agent_id.lower().replace("_", "-")           # "PolicyAgent" → "policyagent"
        agent_id_norm_compact = agent_id_norm_slug.replace("-", "")       # "policy-agent" → "policyagent"

        def _matches(s: set) -> bool:
            return (
                agent_id in s
                or agent_id_norm_slug in s
                or agent_id_norm_compact in s
            )

        # 0. STP agents — hard-route to in-process embedded demo data
        #    (or to Foundry Agent Service runtimes once deploy_stp_agents.py has run and
        #    real ARNs replace the PLACEHOLDER stubs). This skips keyword
        #    matchers that would otherwise grab "policy" or "contract".
        if _matches(self.STP_AGENT_IDS):
            return await self._invoke_stp_agent(
                agent_id, prompt,
                session_id=session_id,
                model_overrides=model_overrides,
            )

        # 0a-EPROD. EPROD agents — hard-route to Foundry Agent Service runtimes.
        # The 6 EPROD agents are READY in us-east-1 (deployed 2026-05-27 via
        # deploy_eprod_foundry_agent.py). Without this hard-route, ids like
        # 'eprod-quote-agent' or 'eprod-tariff-agent' could be grabbed by
        # CBB / aerospace / CRE keyword matchers (substring `quote`, `tariff`,
        # `lease`-adjacent) and routed to the wrong runtime.
        if _matches(self.EPROD_AGENT_IDS):
            # Skip Foundry Agent Service — the 6 EPROD runtimes are deployed but their
            # cold-start exceeds the 30s ceiling, which saturates the backend
            # under any concurrent load (e.g. when multiple chat tabs are
            # open in the demo). Go straight to the in-process simulator for
            # sub-50ms deterministic responses. Foundry Agent Service stays deployed
            # (we're paying for it); flip the conditional below to re-enable
            # the live runtimes once the cold-start is debugged separately.
            #
            #   ENABLE_EPROD_FOUNDRY_AGENT = False   <-- flip to True to re-test
            ENABLE_EPROD_FOUNDRY_AGENT = False
            if ENABLE_EPROD_FOUNDRY_AGENT:
                eprod_arn = (
                    self.AGENT_ARNS.get(agent_id_norm_slug)
                    or self.AGENT_ARNS.get(agent_id_norm_compact)
                    or self.AGENT_ARNS.get(agent_id)
                )
                if eprod_arn:
                    try:
                        result = await self._invoke_runtime(
                            eprod_arn, multi_turn_prompt, session_id=session_id
                        )
                        if result.get("success"):
                            return result
                    except Exception as e:
                        print(f"[eprod-router] Foundry Agent Service exception for {agent_id}: {e}")
            # Always reach the simulator — sub-50ms, deterministic demo answers.
            return self._invoke_eprod_simulator(agent_id_norm_slug, prompt)

        # 0a-CWFCU. CommunityWide FCU agents — hard-route to in-process
        # simulator. The 5 agents (Onboarding, Compliance, Loan Document,
        # Vendor & Contract, Policy & HR) are NOT deployed to Foundry Agent Service for
        # round 1 of this customer demo (per the user's "skip Azure ML /
        # Foundry Agent Service for now" directive). Simulator returns sub-50ms,
        # deterministic, FinCEN-/NCUA-grade responses anchored on the
        # corpus described in synthetic-data/cwfcu/.
        if _matches(self.CWFCU_AGENT_IDS):
            return self._invoke_cwfcu_simulator(agent_id_norm_slug, prompt)

        # 0a-BOLER. The Boler Company agents — hard-route to in-process
        # simulator. 5 agents (Benefits Allocation, Exception Resolution,
        # Journal Entry, Signal, Audit Lens) covering benefits allocation
        # across 5 divisions / 847 employees. Same skip-Foundry Agent Service-for-now
        # directive as CWFCU.
        if _matches(self.BOLER_AGENT_IDS):
            return self._invoke_boler_simulator(agent_id_norm_slug, prompt)

        # 0a-VERIZON. Verizon Far Edge agents — hard-route to in-process
        # simulator anchored on James Patchett's REAL firmware corpus (118
        # reports · HPE Edgeline E910t/E920t/E930t · ZT Proteus/Triton/Galene
        # · Dell R7615). Guarantees the 4 agents (Certification, SchemaWatch,
        # UpgradeAdvisor, Mentor) work offline with zero Foundry Agent Service dependency.
        if _matches(self.VERIZON_AGENT_IDS):
            return self._invoke_verizon_simulator(agent_id_norm_slug, prompt)

        # 0b. Agentic Enterprise (66 Degrees vendor-neutral demos).
        #
        # Two-mode routing (mirrors the STP pattern):
        #   1. PRODUCTION — Foundry Agent Service runtime ARN registered (not PLACEHOLDER):
        #      delegate to _invoke_runtime. The deployed Strands agent
        #      reads the same synthetic-data files (bundled into its ZIP).
        #   2. DEMO (offline) — no ARN registered yet, OR the Foundry Agent Service call
        #      returns an error: fall through to the in-process simulator in
        #      services/agentic_enterprise_demo.py. Sub-50ms, deterministic.
        #
        # This belt-and-suspenders means the demo is always live: if Foundry Agent Service
        # has issues mid-presentation, the simulator picks up seamlessly with
        # the same synthetic-data source.
        if _matches(self.AGENTIC_ENTERPRISE_AGENT_IDS):
            ae_arn = (
                self.AGENT_ARNS.get(agent_id_norm_slug)
                or self.AGENT_ARNS.get(agent_id_norm_compact)
                or self.AGENT_ARNS.get(agent_id)
            )
            if ae_arn and "PLACEHOLDER" not in ae_arn:
                try:
                    result = await self._invoke_runtime(
                        ae_arn, multi_turn_prompt, session_id=session_id
                    )
                    if result.get("success"):
                        return result
                    # Foundry Agent Service returned non-success — log and fall through
                    # to the in-process simulator so the demo never dead-ends.
                except Exception as e:
                    print(f"[ae-router] Foundry Agent Service invocation failed for {agent_id}: {e}; "
                          "falling back to in-process simulator")
            return await self._invoke_agentic_enterprise_demo(
                agent_id, prompt, session_id=session_id
            )

        # 1. CBB agents — hard-route to their own runtimes.
        if agent_id in self.CBB_AGENT_IDS:
            cbb_arn = self.AGENT_ARNS.get(agent_id)
            if cbb_arn:
                try:
                    result = await self._invoke_runtime(
                        cbb_arn, multi_turn_prompt, session_id=session_id
                    )
                    if result.get("success"):
                        return result
                    # Foundry Agent Service error — surface it, don't pretend everything's fine with CRE text.
                    return {
                        "success": False,
                        "response": self._format_foundry_agent_error(agent_id, result),
                        "error": result.get("error", "Foundry Agent Service invocation failed"),
                        "reasoning": [],
                        "actions_taken": [],
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "response": f"I hit an error reaching the {agent_id} runtime on Foundry Agent Service: {e}. Try again in a moment, or check the runtime status in the Azure OpenAI console.",
                        "error": str(e),
                        "reasoning": [],
                        "actions_taken": [],
                    }

        # 2. Aerospace (by keyword).
        if self._is_aerospace_agent(agent_id):
            agent_type = self._get_aerospace_agent_type(agent_id)
            return await self._invoke_aerospace_demo(multi_turn_prompt, agent_type)

        # 3. CRE underwriting (by keyword).
        if self._is_cre_underwriting_agent(agent_id):
            # The CRE demo bot keeps its own in-process state keyed off deal
            # ids, so we feed it only the current user message. History from
            # chat.py isn't needed for its follow-up detection logic.
            return await self._invoke_cre_demo(prompt)

        # 4. ARN match.
        agent_resource_id = self.AGENT_ARNS.get(agent_id)
        if agent_resource_id:
            try:
                result = await self._invoke_runtime(
                    agent_resource_id, multi_turn_prompt, session_id=session_id
                )
                if result.get("success"):
                    return result
                return {
                    "success": False,
                    "response": self._format_foundry_agent_error(agent_id, result),
                    "error": result.get("error", "Foundry Agent Service invocation failed"),
                    "reasoning": [],
                    "actions_taken": [],
                }
            except Exception as e:
                return {
                    "success": False,
                    "response": f"Error reaching Foundry Agent Service runtime for {agent_id}: {e}",
                    "error": str(e),
                    "reasoning": [],
                    "actions_taken": [],
                }

        # 5. Unknown id — give an honest answer, NOT generic CRE text.
        return {
            "success": False,
            "response": (
                f"I don't have a deployed Foundry Agent Service runtime registered for '{agent_id}'. "
                "Add it to backend/services/foundry_agent.py::FoundryAgentService.AGENT_ARNS "
                "or deploy one via foundry_agent-agents/deploy_cbb_agents.py."
            ),
            "error": f"unknown_agent_id:{agent_id}",
            "reasoning": [],
            "actions_taken": [],
        }

    @staticmethod
    def _extract_agent_text(response_data: Any) -> str:
        """Pull the human-readable reply out of a Strands or legacy agent response.

        Shapes handled:
          {"result": {"role": "assistant", "content": [{"text": "..."}]}}   — strands
          {"result": "..."}                                                   — simple
          {"response": "..."}                                                 — legacy
          "..."                                                              — raw string
        """
        if isinstance(response_data, str):
            return response_data

        if not isinstance(response_data, dict):
            return str(response_data)

        # Legacy key
        legacy = response_data.get("response")
        if isinstance(legacy, str) and legacy:
            return legacy

        # Strands/new
        result = response_data.get("result", response_data)
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            content = result.get("content")
            if isinstance(content, list):
                parts = []
                for c in content:
                    if isinstance(c, dict) and "text" in c:
                        parts.append(str(c["text"]))
                    elif isinstance(c, str):
                        parts.append(c)
                text = "\n".join(p for p in parts if p).strip()
                if text:
                    return text
            if isinstance(content, str):
                return content
            # Nothing we recognised — show JSON so debugging is possible
            try:
                return json.dumps(result, indent=2)
            except Exception:
                return str(result)

        return ""

    @staticmethod
    def _extract_agent_reasoning(response_data: Any) -> tuple:
        """Pull structured reasoning steps + actions taken out of a Strands response.

        Strands responses can include <thinking>...</thinking> blocks in text
        and, when the agent uses tools, additional `toolUse` / `toolResult`
        blocks in the content array. We convert both into a flat timeline of
        reasoning steps the Audit Lens renders verbatim.

        Returns:
            (reasoning: list[dict], actions_taken: list[str])
            Each reasoning step is {step, kind, text, action?}.
            actions_taken is the ordered list of unique tool names invoked.
        """
        reasoning: List[Dict[str, Any]] = []
        actions_ordered: List[str] = []

        if not isinstance(response_data, dict):
            return reasoning, actions_ordered

        result = response_data.get("result", response_data)
        if not isinstance(result, dict):
            return reasoning, actions_ordered

        content = result.get("content", [])
        if not isinstance(content, list):
            return reasoning, actions_ordered

        step = 0
        for c in content:
            if not isinstance(c, dict):
                continue
            # Tool invocation
            if "toolUse" in c and isinstance(c["toolUse"], dict):
                step += 1
                tu = c["toolUse"]
                name = tu.get("name") or "unknown_tool"
                if name not in actions_ordered:
                    actions_ordered.append(name)
                reasoning.append({
                    "step": step,
                    "kind": "action",
                    "action": name,
                    "text": f"Called tool `{name}`",
                    "input": tu.get("input") or tu.get("toolUseId") or {},
                })
                continue
            if "toolResult" in c and isinstance(c["toolResult"], dict):
                step += 1
                tr = c["toolResult"]
                reasoning.append({
                    "step": step,
                    "kind": "observation",
                    "text": "Tool returned a result",
                    "output": tr.get("content") or tr.get("output") or {},
                })
                continue
            # Plain text — may contain <thinking> block
            text_val = c.get("text") if "text" in c else None
            if isinstance(text_val, str) and text_val:
                # Split out <thinking>...</thinking> segments as reasoning,
                # the rest as the final answer.
                import re as _re
                m = _re.search(r"<thinking>(.*?)</thinking>", text_val, _re.S | _re.I)
                if m:
                    step += 1
                    reasoning.append({
                        "step": step,
                        "kind": "thought",
                        "text": m.group(1).strip(),
                    })
                remainder = _re.sub(r"<thinking>.*?</thinking>", "", text_val, flags=_re.S | _re.I).strip()
                if remainder:
                    step += 1
                    reasoning.append({
                        "step": step,
                        "kind": "answer",
                        "text": remainder,
                    })
        return reasoning, actions_ordered

    @staticmethod
    def _format_foundry_agent_error(agent_id: str, result: Dict[str, Any]) -> str:
        """User-facing error for an Foundry Agent Service call that came back with success=False."""
        err = result.get("error", "unknown Foundry Agent Service error")
        return (
            f"Foundry Agent Service runtime for **{agent_id}** returned an error:\n\n`{err}`\n\n"
            "Check the runtime status in the Azure OpenAI console or re-deploy via "
            "`foundry_agent-agents/deploy_cbb_agents.py`."
        )

    async def _invoke_aerospace_demo(self, prompt: str, agent_type: str = "contract") -> Dict[str, Any]:
        """Generate intelligent aerospace/defense response for demo."""
        try:
            response = self.aerospace_bot.generate_response(prompt, agent_type)

            # Generate contextual reasoning
            reasoning_steps = [
                {
                    "step": 1,
                    "thought": f"Analyzing aerospace query for {agent_type} operations",
                    "action": "intent_classification"
                },
                {
                    "step": 2,
                    "thought": "Searching contract database and production records",
                    "action": "data_retrieval"
                },
                {
                    "step": 3,
                    "thought": "Applying DFARS/ITAR compliance rules",
                    "action": "compliance_check"
                },
                {
                    "step": 4,
                    "thought": "Generating response with aerospace domain knowledge",
                    "action": "response_generation"
                }
            ]

            return {
                "success": True,
                "response": response,
                "reasoning": reasoning_steps,
                "actions_taken": [step["action"] for step in reasoning_steps],
                "context": {
                    "agent_type": agent_type,
                    "domain": "aerospace_defense"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }

    async def _invoke_agentic_enterprise_demo(
        self,
        agent_id: str,
        prompt: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route to the agentic_enterprise in-process simulators.

        These are the three vendor-neutral demos (supply chain orchestrator,
        cruise concierge, lease extraction) used in the 66 Degrees interview.
        All three read from synthetic-data/agentic_enterprise/*.json — no
        hardcoded business data in the agent code itself.
        """
        try:
            from services.agentic_enterprise_demo import (
                OrchestratorAgent, ConciergeAgent, LeaseAgent,
            )
        except ImportError as e:
            return {
                "success": False,
                "response": f"Agentic Enterprise demo module not loadable: {e}",
                "error": str(e),
                "reasoning": [],
                "actions_taken": [],
            }

        norm = agent_id.lower().replace("_", "-")
        if norm in {"orchestrator-agent", "orchestratoragent", "orchestrator", "supply-orchestrator"}:
            return OrchestratorAgent.respond(prompt)
        if norm in {"concierge-agent", "conciergeagent", "concierge", "cruise-concierge"}:
            return ConciergeAgent.respond(prompt, session_id=session_id or "default")
        if norm in {"lease-agent", "leaseagent", "lease"}:
            return LeaseAgent.respond(prompt)
        return {
            "success": False,
            "response": f"Unknown agentic_enterprise agent id: {agent_id}",
            "error": f"unknown_agent_id:{agent_id}",
            "reasoning": [],
            "actions_taken": [],
        }

    async def _invoke_cre_demo(self, prompt: str) -> Dict[str, Any]:
        """Generate intelligent CRE underwriting response for demo."""
        try:
            # Get current context for reasoning
            context = CREUnderwritingBot._conversation_state
            current_deal = context.get("last_deal_id")
            current_topic = context.get("last_topic")

            response = self.cre_bot.generate_response(prompt)

            # Generate contextual reasoning
            reasoning_steps = []

            # Step 1: Understand intent
            if self.cre_bot._is_follow_up(prompt):
                reasoning_steps.append({
                    "step": 1,
                    "thought": f"Detected follow-up to previous query about {current_deal or 'queue'}",
                    "action": "context_retrieval"
                })
            else:
                reasoning_steps.append({
                    "step": 1,
                    "thought": f"Analyzing new query: '{prompt[:50]}...'",
                    "action": "intent_classification"
                })

            # Step 2: Identify deal
            new_deal = CREUnderwritingBot._conversation_state.get("last_deal_id")
            if new_deal:
                deal_info = CREUnderwritingKnowledgeBase.PROCESSED_DEALS.get(new_deal, {})
                reasoning_steps.append({
                    "step": 2,
                    "thought": f"Identified submission: {deal_info.get('name', new_deal)} (TIV: ${deal_info.get('tiv', 0):,})",
                    "action": "deal_lookup"
                })

            # Step 3: Apply underwriting analysis
            new_topic = CREUnderwritingBot._conversation_state.get("last_topic")
            topic_descriptions = {
                "risk": "Evaluating risk factors and calculating weighted score",
                "premium": "Computing premium based on rates, experience, and adjustments",
                "loss": "Analyzing 5-year claims history and loss trends",
                "decision": "Applying underwriting guidelines and authority levels",
                "overview": "Compiling submission summary and key metrics",
                "full_details": "Generating comprehensive analysis across all dimensions"
            }
            if new_topic:
                reasoning_steps.append({
                    "step": 3,
                    "thought": topic_descriptions.get(new_topic, "Processing underwriting query"),
                    "action": f"{new_topic}_analysis"
                })

            # Step 4: Generate response
            reasoning_steps.append({
                "step": len(reasoning_steps) + 1,
                "thought": "Formulating response with actionable insights",
                "action": "response_generation"
            })

            return {
                "success": True,
                "response": response,
                "reasoning": reasoning_steps,
                "actions_taken": [step["action"] for step in reasoning_steps],
                "context": {
                    "deal_id": new_deal,
                    "topic": new_topic
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }

    @staticmethod
    def _build_multi_turn_prompt(
        prompt: str, history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Fold prior turns into a single prompt string so Strands agents
        (which read `payload["prompt"]` as a flat string) still see context.

        Output shape:
            Previous conversation:
            User: <content>
            Assistant: <content>
            User: <content>
            Assistant: <content>

            Current user message:
            <prompt>

        Returns the raw prompt unchanged when no history is supplied so the
        first turn of a session looks identical to the legacy behavior.
        """
        if not history:
            return prompt

        lines = ["Previous conversation:"]
        for turn in history:
            role = "User" if turn.get("role") == "user" else "Assistant"
            body = (turn.get("content") or "").strip()
            if not body:
                continue
            # Flatten any embedded newlines so the role boundary stays clear
            body = body.replace("\n", " ")
            # Per-turn cap keeps one runaway answer from eating the window.
            if len(body) > 1200:
                body = body[:1200] + "…"
            lines.append(f"{role}: {body}")

        lines.append("")
        lines.append("Current user message:")
        lines.append(prompt)
        return "\n".join(lines)

    # ─────────────────────── STP demo invocation ────────────────────────
    #
    # Two-mode invoker:
    #   1. PRODUCTION — Foundry Agent Service runtime ARN is registered (no PLACEHOLDER):
    #      delegate to _invoke_runtime. This is what runs after
    #      `python3 deploy_stp_agents.py --apply` lands the real ARNs.
    #
    #   2. DEMO (default tonight) — runtime ARN is still a placeholder:
    #      compose the response in-process by calling the relevant action
    #      handlers directly. No Azure OpenAI LLM call, no Strands dependency,
    #      no Docker container, no network hop. Sub-100ms response, fully
    #      deterministic — exactly what the demo needs.
    #
    # The deterministic composer mirrors the agent's system-prompt template
    # so the user sees the same response shape either way.
    #
    async def _invoke_stp_agent(
        self,
        agent_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        model_overrides: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Invoke an STP agent — Foundry Agent Service if deployed, in-process composer otherwise.

        `model_overrides` carries per-agent per-slot Azure OpenAI model picks from
        the user's Settings → Agent Models panel. Forwarded into the runtime
        payload as `model_overrides`; the agent reads payload["model_overrides"]
        and switches AzureOpenAIModel per task. The in-process composer also
        reads it to annotate the audit log with the chosen model_id.
        """
        norm = agent_id.replace("_", "-").lower()

        # Production path — real Foundry Agent Service runtime ARN registered.
        # Pass model_overrides through the payload so the runtime can use it.
        arn = self.AGENT_ARNS.get(norm, "")
        if arn and "PLACEHOLDER" not in arn:
            return await self._invoke_runtime(
                arn, prompt,
                session_id=session_id,
                extra_payload={"model_overrides": model_overrides} if model_overrides else None,
            )

        # Demo path — deterministic in-process composer
        return self._compose_stp_response(
            norm, prompt,
            session_id=session_id,
            model_overrides=model_overrides,
        )

    def _compose_stp_response(
        self,
        norm_agent_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        model_overrides: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Deterministic composer that calls action handlers and stitches the response.

        For each STP agent type we know which handlers to call and how to
        format the output to match the agent's system-prompt expectations.
        Tools come straight from `actions/nuclear_operations/*/handler.py` —
        the same handlers Lambda runs in production.

        `model_overrides` (from Settings → Agent Models) is recorded against
        each reasoning step so the DVR + Cost-per-Query tile can show
        per-step model + cost — even though the composer is offline and
        doesn't actually call the LLM.
        """
        # Resolve which model would have been used for each slot of this
        # agent, given the user's overrides. Used for audit-log annotation.
        try:
            from services.model_registry import resolve_model_for_agent_slot
        except ImportError:
            resolve_model_for_agent_slot = None  # type: ignore

        def _model_for(slot_key: str) -> Dict[str, Any]:
            """Return {id, display_name, cost_estimate} for the given slot."""
            if resolve_model_for_agent_slot is None:
                return {"model_id": "(registry-unavailable)", "model_display": "(registry-unavailable)", "cost_usd": 0.0}
            spec = resolve_model_for_agent_slot(norm_agent_id, slot_key, model_overrides)
            tokens_in, tokens_out = (2500, 400) if slot_key == "synthesis" else (1500, 200)
            cost = (spec.input_cost_per_1m_usd * tokens_in + spec.output_cost_per_1m_usd * tokens_out) / 1_000_000
            return {
                "model_id": spec.id,
                "model_display": spec.display_name,
                "cost_usd": round(cost, 5),
            }
        # Add aws/ root to sys.path so `actions.nuclear_operations.*` resolves.
        # The backend lives at aws/backend/ — parents[2] of this file is aws/.
        _aws_root = str(Path(__file__).resolve().parents[2])
        if _aws_root not in sys.path:
            sys.path.insert(0, _aws_root)

        # Lazy-import handlers so the composer has zero impact on cold start
        from actions.nuclear_operations.policy_search.handler import policy_search
        from actions.nuclear_operations.policy_cite_extract.handler import policy_cite_extract
        from actions.nuclear_operations.oracle_pm_lookup.handler import oracle_pm_lookup
        from actions.nuclear_operations.engineer_attribution.handler import engineer_attribution
        from actions.nuclear_operations.wp_attachment_fetch.handler import wp_attachment_fetch
        from actions.nuclear_operations.wp_corpus_search.handler import wp_corpus_search
        from actions.nuclear_operations.failure_mode_aggregate.handler import failure_mode_aggregate
        from actions.nuclear_operations.rul_predict.handler import rul_predict
        from actions.nuclear_operations.anomaly_detect.handler import anomaly_detect
        from actions.nuclear_operations.pm_recommend.handler import pm_recommend
        from actions.nuclear_operations.risk_score_compute.handler import risk_score_compute
        from actions.nuclear_operations.intent_classify.handler import intent_classify

        actions_taken: List[str] = []
        reasoning: List[Dict[str, Any]] = []

        def step(idx: int, kind: str, action: str, text: str, output: Any = None,
                 slot: str = "tool_selection") -> None:
            entry = {
                "step": idx, "kind": kind, "action": action, "text": text,
                "output": output if isinstance(output, (str, int, float, bool)) else None,
            }
            # Annotate with model_id + cost for the DVR / Cost-per-Query tile.
            # Pure thinking steps (no tool call) bill against tool_selection slot
            # of the current agent — that's the model the LLM would have used
            # to "think" if this were the live Foundry Agent Service path.
            if kind in ("action", "thinking"):
                m = _model_for(slot)
                entry.update(m)
            reasoning.append(entry)
            if kind == "action" and action not in actions_taken:
                actions_taken.append(action)

        # ── ChatSTP router — classify and delegate ─────────────────────
        if norm_agent_id in ("chatstp", "chatstp-router"):
            step(1, "thinking", "", "Classifying user query intent…")
            cls = intent_classify(query=prompt)
            step(2, "action", "intent_classify",
                 f"Detected intent: {cls.get('intent')} (conf {cls.get('confidence')})")
            intent = cls.get("intent")
            entities = cls.get("entities_extracted", {})
            target_agent = {
                "policy_lookup":          "policy-agent",
                "maintenance_history":    "maintenance-agent",
                "issue_analysis":         "diagnostics-agent",
                "predictive_maintenance": "reliability-agent",
            }.get(intent)

            if not target_agent:
                return {
                    "success": True,
                    "response": (
                        "I'm focused on STP plant operations — try asking me about a policy, "
                        "an equipment item (P-3A, EDG-2, MOV-7B), failure history, or "
                        "predictive maintenance for an asset."
                    ),
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            step(3, "thinking", "", f"Delegating to {target_agent}")
            sub = self._compose_stp_response(target_agent, prompt, session_id=session_id)
            # Merge router reasoning ahead of specialist's
            if isinstance(sub.get("reasoning"), list):
                sub["reasoning"] = reasoning + [
                    {**r, "step": r.get("step", 0) + 3} for r in sub["reasoning"]
                ]
            sub["actions_taken"] = list(dict.fromkeys(actions_taken + sub.get("actions_taken", [])))
            return sub

        # ── PolicyAgent (UC-1) ─────────────────────────────────────────
        if norm_agent_id in ("policy-agent", "policyagent"):
            step(1, "action", "policy_search", f"Searching policy corpus for: {prompt!r}")
            results = policy_search(query=prompt, top_k=1)
            if results.get("status") != "ok" or not results.get("results"):
                return {
                    "success": True,
                    "response": "No policy on file matches that query. Try rephrasing or naming the doc number directly.",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            top = results["results"][0]
            step(2, "action", "policy_cite_extract",
                 f"Extracting verbatim text from {top['doc_number']}")
            cite = policy_cite_extract(doc_id=top["doc_id"], topic=prompt)
            answer = (
                f"{cite.get('verbatim_text', '')}\n\n"
                f"**Source: {cite.get('citation_string')} · owner: {cite.get('owner')}**"
            )
            return {
                "success": True, "response": answer,
                "reasoning": reasoning, "actions_taken": actions_taken,
            }

        # ── MaintenanceAgent (UC-2) ────────────────────────────────────
        if norm_agent_id in ("maintenance-agent", "maintenanceagent"):
            cls = intent_classify(query=prompt)
            equipment_ids = cls.get("entities_extracted", {}).get("equipment_ids", [])
            if not equipment_ids:
                return {
                    "success": True,
                    "response": "Which equipment? Tell me an id (e.g. P-3A, EDG-2, MOV-7B) and I can pull the PM history.",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            eq = equipment_ids[0]
            step(1, "action", "oracle_pm_lookup", f"Querying Oracle PMHISTORY for {eq}")
            pm = oracle_pm_lookup(equipment_id=eq, lookback_days=365)
            if pm.get("status") != "ok" or not pm.get("last_pm_wo_id"):
                return {
                    "success": True,
                    "response": f"No completed PMs found for {eq} in the last 365 days.",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            step(2, "action", "engineer_attribution",
                 f"Attributing {pm['last_pm_wo_id']} to technicians + lead engineer")
            attr = engineer_attribution(wo_id=pm["last_pm_wo_id"])
            step(3, "action", "wp_attachment_fetch", "Resolving work-package PDF link")
            wp = wp_attachment_fetch(wo_id=pm["last_pm_wo_id"])
            tech_names = ", ".join([t.get("name", t.get("employee_id", "?"))
                                    for t in attr.get("technicians", [])])
            lead_name = (attr.get("lead_engineer") or {}).get("name", "—")
            answer = (
                f"Last PM on **{eq}**: **{pm['last_pm_date']}** ({pm['last_pm_wo_id']})\n"
                f"Performed by: **{lead_name}** with {tech_names}\n"
                f"Procedure: {pm.get('pm_template_id')} per {pm.get('regulatory_basis')} "
                f"· {pm.get('procedure_doc')}\n"
                f"Next PM due: **{pm.get('next_pm_due')}**\n\n"
                f"📎 Work Package: {wp.get('s3_url', '(not available)')}"
            )
            return {
                "success": True, "response": answer,
                "reasoning": reasoning, "actions_taken": actions_taken,
            }

        # ── DiagnosticsAgent (UC-3) ────────────────────────────────────
        if norm_agent_id in ("diagnostics-agent", "diagnosticsagent"):
            cls = intent_classify(query=prompt)
            equipment_ids = cls.get("entities_extracted", {}).get("equipment_ids", [])
            if not equipment_ids:
                return {
                    "success": True,
                    "response": "Which equipment or system? Give me an id (e.g. P-3A) or a system code (RCS, EDG, ESW).",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            eq = equipment_ids[0]
            step(1, "action", "wp_corpus_search", f"Scanning work-package corpus for {eq}")
            wps = wp_corpus_search(equipment_id=eq)
            modes = wps.get("failure_modes_observed", [])
            if not modes:
                return {
                    "success": True,
                    "response": f"No failure history indexed for {eq}.",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            lines = [f"**Top issues for {eq}** ({wps.get('total_failure_events', 0)} events analyzed across {wps.get('total_packages_indexed', 0)} work packages):\n"]
            for i, m in enumerate(modes[:5], start=1):
                cited = ", ".join(m.get("cited_wo_ids", [])[:3]) or "—"
                miti  = (m.get("mitigation_actions") or ["—"])[0]
                lines.append(
                    f"{i}. **{m.get('mode_name')}** — {m.get('count')} events "
                    f"({m.get('percentage')}%) — typical lead {m.get('typical_lead_days')}d. "
                    f"Mitigation: {miti}. Cited from: {cited}"
                )
            step(2, "action", "failure_mode_aggregate",
                 f"{len(modes)} modes ranked, top {min(5, len(modes))} returned")
            return {
                "success": True, "response": "\n".join(lines),
                "reasoning": reasoning, "actions_taken": actions_taken,
            }

        # ── ReliabilityAgent (UC-4) ────────────────────────────────────
        if norm_agent_id in ("reliability-agent", "reliabilityagent"):
            cls = intent_classify(query=prompt)
            equipment_ids = cls.get("entities_extracted", {}).get("equipment_ids", [])
            if not equipment_ids:
                return {
                    "success": True,
                    "response": "Which equipment? Tell me an id (e.g. P-3A) and I'll run the predictive stack.",
                    "reasoning": reasoning, "actions_taken": actions_taken,
                }
            eq = equipment_ids[0]
            step(1, "action", "anomaly_detect", f"Scanning sensor streams for {eq} (last 14 days)")
            an = anomaly_detect(equipment_id=eq, lookback_days=14)
            step(2, "action", "rul_predict", "Forecasting RUL with 80%/95% bands")
            rul = rul_predict(equipment_id=eq, horizon_days=30)
            step(3, "action", "risk_score_compute", "Computing composite risk score")
            risk = risk_score_compute(equipment_id=eq)
            step(4, "action", "pm_recommend", "Translating risk into PM-advance recommendation")
            rec = pm_recommend(equipment_id=eq)

            audit_id = f"AUD-{(session_id or 'demo')[:8]}-{int(__import__('time').time())}"
            scripted = (rul.get("scripted_message") or rec.get("scripted_message") or "").strip()
            avoidance = rec.get("estimated_avoidance", {}) or {}
            answer_lines = [
                f"**{risk.get('risk_tier', 'unknown').upper()}: {eq} — risk score {risk.get('risk_score', 0)}/100**",
                f"Predicted failure: {rul.get('days_until_failure', '?')}d "
                f"(80% CI {rul.get('confidence_lower_80')}–{rul.get('confidence_upper_80')}d, "
                f"95% CI {rul.get('confidence_lower_95')}–{rul.get('confidence_upper_95')}d)",
                f"Recommended action: {rec.get('recommendation', '—')} "
                f"Estimated avoidance: ${avoidance.get('cost_usd', 0):,}, {avoidance.get('downtime_hours', 0)}h.",
            ]
            if scripted:
                answer_lines.append(f"\n{scripted}")
            answer_lines.append(f"\n[Decision logged to apex.audit_log: {audit_id}]")
            return {
                "success": True, "response": "\n".join(answer_lines),
                "reasoning": reasoning, "actions_taken": actions_taken,
            }

        return {
            "success": False,
            "response": f"Unknown STP agent id: {norm_agent_id}",
            "error": "unknown_stp_agent",
            "reasoning": reasoning, "actions_taken": actions_taken,
        }

    def _invoke_eprod_simulator(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """Deterministic in-process simulator for the 6 EPROD agents.

        Returns demo-quality answers based on (agent_id, prompt keywords).
        Triggers when Foundry Agent Service cold-start exceeds the 30s ceiling — keeps
        the chat alive during demos. Same pattern as the Agentic Enterprise
        fallback in services/agentic_enterprise_demo.py.

        Each branch crafts a midstream-realistic answer with vendor names,
        MSA refs, asset codes, AFE numbers, and dollar amounts that match
        the rest of the EPROD demo data.
        """
        p = (prompt or "").lower()

        # ── InvoiceAgent ────────────────────────────────────────────────
        if "invoice" in agent_id:
            if "halliburton" in p or "$50" in p or "50k" in p:
                response = (
                    "Found 3 Halliburton invoices over $50K from April 2026:\n"
                    "  • INV-HAL-2026-04-3847 · $184,500 · PO-MATCHED to PO-2026-EPC-4521\n"
                    "  • INV-HAL-2026-04-3719 · $98,200  · PO-MATCHED to PO-2026-OPS-2189\n"
                    "  • INV-HAL-2026-04-2611 · $62,400  · ⚠ NO PO REFERENCE — flagged HITL-high\n\n"
                    "Average confidence 96.2%. Rate variance against MSA-HAL-2024-03 within "
                    "±2% tolerance for all 3. Recommend approving 2, holding 1 for HITL."
                )
            elif "msa-hal-2024-03" in p or ("rate variance" in p and "hal" in p):
                response = (
                    "12 invoices this month show rate variance > 2% vs MSA-HAL-2024-03 rate card:\n"
                    "  • 4 invoices billed above MSA (Schlumberger +6.1%, Halliburton +4.2%, etc.)\n"
                    "  • 8 invoices billed below MSA (likely vendor concessions)\n"
                    "  • Total exposure: $284K if not contested\n"
                    "  • Already auto-flagged in HITL queue under category=rate_variance"
                )
            elif "baker hughes" in p or "ndt" in p or "hot-tap" in p or "hot tap" in p:
                response = (
                    "Latest Baker Hughes NDT invoice — INV-BHI-2026-05-1187 (Mont Belvieu hot-tap, EPD-PL-MB-04):\n"
                    "  • Line 1 · UT shear-wave inspection · 84 hrs × $185/hr = $15,540\n"
                    "  • Line 2 · Phased-array technician (Level III) · 36 hrs × $245/hr = $8,820\n"
                    "  • Line 3 · Mobilization + rig-up (lump sum) = $4,800\n"
                    "  • Line 4 · Consumables (couplant, film) = $1,212\n"
                    "Total $30,372 · MSA-BHI-2025-01 rate-card match 100% · auto-approved to AFE-2025-0341."
                )
            elif "inv-slb-26-0418" in p or "slb-26-0418" in p or "schlumberger" in p:
                response = (
                    "Validated INV-SLB-26-0418 ($217,400) against MSA-SLB-2025-0112 rate card:\n"
                    "  • Wireline logging crew: 72 hrs × $385/hr — MSA $362/hr → +6.4% variance (above tolerance)\n"
                    "  • Tool rental (downhole gauge): $48,200 — MSA lump-sum $45,000 → +7.1%\n"
                    "  • Mobilization: $12,800 — within MSA flat rate band\n"
                    "Net overage vs MSA: $14,840. Routed to HITL-rate-variance queue, SLA 24 hrs."
                )
            elif "afe" in p and ("missing" in p or "blocked" in p or "references this" in p):
                response = (
                    "9 AP invoices blocked this week on missing AFE references (total $312,840):\n"
                    "  • 4 Halliburton invoices · Sweeny lateral · awaiting AFE-2024-0882 tie-out\n"
                    "  • 3 Cameron Int'l invoices · Mont Belvieu compressor · AFE-2025-0341 not cited\n"
                    "  • 2 ChemTreat invoices · operating spend · need cost-center recode\n"
                    "All sitting in HITL queue category=missing_afe. Avg age 2.3 days. SLA breach in 18 hrs."
                )
            elif "kiewit" in p and ("escalation" in p or "cap" in p):
                response = (
                    "4 Kiewit invoices billed above MSA-KIEWIT-2024-07 escalation cap (3% PPI-FG):\n"
                    "  • INV-KIE-2026-05-0814 · $187,400 · billed +5.8% over base rate (cap exceeded by 2.8 pts)\n"
                    "  • INV-KIE-2026-05-0712 · $94,200  · billed +4.2% (cap exceeded by 1.2 pts)\n"
                    "  • INV-KIE-2026-05-0608 · $62,500  · billed +6.1% (cap exceeded by 3.1 pts)\n"
                    "  • INV-KIE-2026-04-0418 · $48,200  · billed +3.9% (cap exceeded by 0.9 pts)\n"
                    "Net excess: $14,820. Routed to HITL-escalation_cap queue for procurement review."
                )
            elif "operating-class" in p or ("operating" in p and "capital" in p) or "capital afe" in p:
                response = (
                    "6 invoices flagged charging operating-class rates against a capital AFE:\n"
                    "  • INV-EMR-2026-05-0418 · Emerson Process · $42,800 → AFE-2025-0341 (capital)\n"
                    "  • INV-ARC-2026-05-0212 · Archrock Services · $18,650 → AFE-2026-0044 (capital)\n"
                    "  • INV-CHT-2026-05-0091 · ChemTreat · $7,920 → AFE-2024-0882 (capital)\n"
                    "Net mis-coding exposure: $84,200. Routed to finance for journal reclass before period close."
                )
            elif "targa" in p or ("mont belvieu" in p and "fractionation" in p) or ("april" in p and "may" in p):
                response = (
                    "Targa Mont Belvieu fractionation invoices · May 2026 vs April 2026:\n"
                    "  • Volume: 18 invoices May ($412K) vs 14 invoices April ($338K) — +21.9% spend\n"
                    "  • Driver: AFE-2025-0341 commissioning ramp on EPD-PROC-MTB-21\n"
                    "  • Avg unit rate held flat (MSA-BHI-2025-01 escalation deferred)\n"
                    "  • 2 May invoices flagged for >5% variance — both Cameron Int'l hot-tap labor\n"
                    "Net month-over-month spend up $74K, all within AFE-2025-0341 approved envelope."
                )
            elif "sweeny" in p or ("marine" in p and "terminal" in p) or "$25k" in p or "25k" in p:
                response = (
                    "Invoices coded to Sweeny marine terminal (EPD-FT-SWY-08) cost center > $25K:\n"
                    "  • INV-KIE-2026-05-0814 · Kiewit · $187,400 · AFE-2024-0882 dock pile-cap repair\n"
                    "  • INV-BEC-2026-05-0277 · Bechtel · $94,600 · loading-arm overhaul (capital)\n"
                    "  • INV-CAM-2026-05-0182 · Cameron Int'l · $48,200 · valve actuator swap\n"
                    "  • INV-WFT-2026-05-0098 · Weatherford · $31,750 · sub-sea hose inspection\n"
                    "All 4 PO-matched, MSA-validated, auto-approved. Total Sweeny marine MTD: $362K."
                )
            elif "fluor" in p or "schedule b" in p:
                response = (
                    "Found 2 Fluor invoices referencing scope outside their executed MSA-FLUOR-2023-11 Schedule B:\n"
                    "  • INV-FLR-2026-05-0612 · $128,400 · line 4 covers HAZOP facilitation — NOT in Schedule B\n"
                    "  • INV-FLR-2026-05-0581 · $42,800  · line 2 covers commissioning support — NOT in Schedule B\n"
                    "Combined exposure: $171,200. Both routed to procurement_exceptions queue. "
                    "Recommend Schedule B amendment before next billing cycle."
                )
            elif "rate variance" in p or "rate mismatch" in p or "msa" in p:
                response = (
                    "12 invoices this month show rate variance > 2% vs MSA rate card:\n"
                    "  • 4 invoices billed above MSA (Schlumberger +6.1%, Halliburton +4.2%, etc.)\n"
                    "  • 8 invoices billed below MSA (likely vendor concessions)\n"
                    "  • Total exposure: $284K if not contested\n"
                    "  • Already auto-flagged in HITL queue under category=rate_variance"
                )
            else:
                response = (
                    "InvoiceAgent processed 1,247 vendor invoices in May 2026 at 94.2% accuracy. "
                    "3 currently in HITL queue (2 rate-variance, 1 missing-PO). "
                    "Routed 14 to AP for rate validation, auto-approved 1,230. "
                    "Ask me about a specific vendor (Halliburton, Schlumberger, Baker Hughes), invoice ID, "
                    "or month-to-date totals."
                )

        # ── POAgent ─────────────────────────────────────────────────────
        elif "po-agent" in agent_id or "poagent" in agent_id or agent_id.endswith("-po-agent"):
            if ("capital scope" in p) or ("capital" in p and "operating afe" in p) or ("operating afe" in p and "bucket" in p):
                response = (
                    "5 POs charging capital scope to an operating AFE bucket:\n"
                    "  • PO-2026-EPC-7218 · Kiewit · $148,200 → AFE-2026-OPS-014 (should be capital AFE-2026-014)\n"
                    "  • PO-2026-EPC-7244 · Bechtel · $84,400 → AFE-2026-OPS-018 (should be AFE-2024-0882)\n"
                    "  • PO-2026-EPC-7261 · Cameron Int'l · $48,200 → AFE-2026-OPS-022 (capital tie-ins)\n"
                    "  • 2 smaller POs ($12K-$28K) with similar mis-coding.\n"
                    "Net capex shifted to opex: $321,000. Routed to finance for journal reclass + AFE re-tagging."
                )
            elif "kiewit" in p or "schedule b" in p or "scope" in p:
                response = (
                    "Found 2 Kiewit POs referencing MSA-KIEWIT-2024-07 but billing outside "
                    "Schedule B scope:\n"
                    "  • PO-2026-EPC-4521 · $412,000 · line 6 covers welding services — NOT in Schedule B\n"
                    "  • PO-2026-EPC-4498 · $187,000 · line 3 covers commissioning support — NOT in Schedule B\n\n"
                    "Both routed to procurement_exceptions queue with category=scope_violation. "
                    "SLA: 8 hrs. Awaiting procurement signoff."
                )
            elif "rate" in p and ("above" in p or "exceed" in p or "5%" in p):
                response = (
                    "Found 8 POs where unit rate is > 5% above contracted MSA rate card:\n"
                    "  • PO-2026-EPC-4521 — line 1: $285K lump-sum vs MSA range $250-300K (within tolerance)\n"
                    "  • PO-2026-CHEM-0892 — line 4: $42/lb vs MSA $38/lb (+10.5%) — HITL flagged\n"
                    "  • PO-2026-OPS-2189 — line 2: $4,520/wk PM vs MSA $4,200/wk (+7.6%) — HITL flagged\n\n"
                    "5 more flagged for procurement review. Combined exposure: $94K/quarter."
                )
            elif "tax" in p:
                response = (
                    "Tax-code mismatch report: 4 POs with TX-I (industrial) where asset code requires "
                    "TX-E (exempt). Combined tax differential: $12,400.\n"
                    "  • PO-2026-08812 Baker Hughes · asset EPD-COMP-Acadian-7\n"
                    "  • PO-2026-08847 Cameron Int'l · asset EPD-PL-MB-04\n"
                    "  • PO-2026-08891 SLB · asset EPD-PL-SE-12\n"
                    "  • PO-2026-08923 Weatherford · asset EPD-COMP-Houston-2"
                )
            elif "halliburton" in p or "$250" in p or "250k" in p or "vp sign" in p or "approval threshold" in p:
                response = (
                    "3 open Halliburton POs exceed the $250K VP approval threshold without VP sign-off:\n"
                    "  • PO-2026-EPC-4521 · $412,000 · MSA-HAL-2024-03 · Sweeny lateral (AFE-2024-0882)\n"
                    "  • PO-2026-OPS-2189 · $298,400 · MSA-HAL-2024-03 · Mont Belvieu turnaround (AFE-2025-0341)\n"
                    "  • PO-2026-CHEM-0892 · $267,800 · MSA-HAL-2024-03 · Permian chemical injection (AFE-2025-1104)\n"
                    "All 3 routed to procurement_signoff_required queue. SLA breach in 14 hrs. "
                    "Recommend escalating to VP-Supply Chain for same-day signature."
                )
            elif "afe-2026-014" in p or "compressor station" in p or "commitment-to-date" in p or "commitment to date" in p:
                response = (
                    "POs tied to AFE-2026-014 (Sweeny compressor station expansion) — 5 active:\n"
                    "  • PO-2026-EPC-7218 · Kiewit · $1,840,000 · committed $1,420,000 (77.2%)\n"
                    "  • PO-2026-EPC-7244 · Bechtel · $920,000 · committed $612,000 (66.5%)\n"
                    "  • PO-2026-EPC-7261 · Cameron Int'l · $487,000 · committed $487,000 (100%)\n"
                    "  • PO-2026-EPC-7277 · Emerson Process · $312,800 · committed $184,200 (58.9%)\n"
                    "  • PO-2026-EPC-7298 · Fluor (engineering) · $248,000 · committed $148,800 (60.0%)\n"
                    "AFE balance: $3,807,800 committed of $4,200,000 approved ($392K remaining)."
                )
            elif "po-26-0419-flr" in p or "0419-flr" in p or ("fluor" in p and ("rate card" in p or "senior process" in p)):
                response = (
                    "PO-26-0419-FLR vs Fluor engineering rate card (MSA-FLUOR-2023-11):\n"
                    "  • Senior process engineer: PO $238/hr vs rate-card $218/hr (+9.2%) — exceeds 5% tolerance\n"
                    "  • EPC project lead: PO $192/hr vs rate-card $185/hr (+3.8%) — within tolerance\n"
                    "  • CAD designer: PO $128/hr vs rate-card $124/hr (+3.2%) — within tolerance\n"
                    "PO total $284,200, scope = HAZOP + P&ID redline for AFE-2025-0341. "
                    "Net variance $4,180. Routed to procurement HITL — recommend negotiating senior PE rate."
                )
            elif "lack" in p or "remediation" in p or "no msa" in p or ("missing" in p and "msa" in p):
                response = (
                    "7 open POs lack a valid MSA reference and need procurement remediation:\n"
                    "  • PO-2026-09112 PIPETECH SVCS LLC · $187,000 · no MSA on file\n"
                    "  • PO-2026-09144 Triad Inspection · $94,800 · MSA expired 2025-12-31\n"
                    "  • PO-2026-09177 Allied Welding · $62,400 · MSA covers TX only, scope in OK\n"
                    "  • PO-2026-09188 Pacific Coatings · $48,200 · MSA missing Schedule B for blasting\n"
                    "  • 3 more under $25K with similar gaps.\n"
                    "Combined exposure: $441,200. Routed to procurement_remediation queue, SLA 5 business days."
                )
            elif "q2 2026" in p or "pipeline integrity" in p or "inspection services" in p:
                response = (
                    "POs issued Q2 2026 for pipeline integrity inspection services — 9 active, $2.84M total:\n"
                    "  • PO-2026-INT-0411 · Baker Hughes · $612,000 · ILI Mont Belvieu lateral (EPD-PL-MB-04)\n"
                    "  • PO-2026-INT-0438 · Schlumberger · $487,500 · caliper run Seaway SE (EPD-PL-SE-12)\n"
                    "  • PO-2026-INT-0462 · Halliburton · $384,200 · MFL inspection Acadian gas\n"
                    "  • PO-2026-INT-0489 · Quest Integrity · $298,400 · cleaning pig + dewatering\n"
                    "  • 5 smaller POs ($75K-$220K) for in-line tools and tethered crawlers.\n"
                    "All MSA-validated, 92.7% PO-MATCH-OK. Avg cycle time 3.8 days."
                )
            elif "unit-of-measure" in p or "uom" in p or ("unit" in p and "mismatch" in p):
                response = (
                    "5 POs with unit-of-measure mismatches between PO header and MSA rate sheet:\n"
                    "  • PO-2026-CHEM-0892 · ChemTreat · MSA $/gal but PO billed $/drum (factor 55x)\n"
                    "  • PO-2026-OPS-2418 · Weatherford · MSA $/ft but PO billed $/m (factor 3.28x)\n"
                    "  • PO-2026-EPC-4498 · Kiewit · MSA $/lift but PO billed $/day (no MSA basis)\n"
                    "  • PO-2026-08847 · Cameron Int'l · MSA $/valve but PO billed lump-sum (no breakdown)\n"
                    "  • PO-2026-NDT-1182 · BHI · MSA $/hr but PO billed $/inspection\n"
                    "Combined billing variance: $42,800. All routed to procurement_uom_review queue."
                )
            elif "bechtel" in p or "marine terminal po" in p or "remaining commitment" in p:
                response = (
                    "Bechtel marine terminal PO commitment status (PO-2026-EPC-7244, EPD-FT-SWY-08):\n"
                    "  • Original PO value: $920,000 · MSA-BECHTEL-2024-04 · AFE-2024-0882\n"
                    "  • Committed (invoices to date): $612,400 (66.6%)\n"
                    "  • Remaining commitment: $307,600\n"
                    "  • Forecast burn through Q3 2026: $284,000 (loading-arm overhaul + commissioning)\n"
                    "Projected $23,600 surplus at PO close. No change order anticipated."
                )
            else:
                response = (
                    "POAgent validated 389 POs in May 2026 at 92.7% accuracy. "
                    "14 mismatches flagged — 4 tax-code, 6 rate-variance, 4 scope-violation. "
                    "Avg cycle time: 4.2 min. Ask me about a vendor (Halliburton, Kiewit, Cameron), "
                    "MSA reference (MSA-KIEWIT-2024-07), or exception type (rate / tax / scope)."
                )

        # ── VendorAgent (Non-PO MSA) ────────────────────────────────────
        elif "vendor" in agent_id:
            if "pipetech" in p or "no msa" in p or ("missing" in p and "msa" in p):
                response = (
                    "⚠ Non-PO submission for 'PIPETECH SVCS LLC' — no active MSA on file.\n"
                    "Amount: $187,000 · Submitted: 2026-05-20 · Requestor: ops@eprod.com\n\n"
                    "Status: HELD for procurement. Action required: create MSA or convert to PO before "
                    "payment. Routed to procurement queue with category=missing_msa, SLA 24 hrs."
                )
            elif "non-po" in p and ("may" in p or "lacked" in p or "validation" in p):
                response = (
                    "Non-PO transactions in May 2026 lacking MSA validation — 6 entries, $342,800 total:\n"
                    "  • PIPETECH SVCS LLC · $187,000 · no MSA on file\n"
                    "  • Triad Inspection · $48,200 · MSA expired 2025-12-31\n"
                    "  • Coastal Crane Rentals · $42,400 · MSA covers LA only, scope was TX\n"
                    "  • Lone Star Electrical · $28,800 · MSA missing insurance addendum\n"
                    "  • Apex Survey Group · $21,200 · MSA scope = surveying, billed as engineering\n"
                    "  • Gulf NDT Services · $15,200 · MSA in draft, never countersigned\n"
                    "All 6 in procurement HITL queue. Auto-payment hold active until MSA cured."
                )
            elif "w-9" in p or "w9" in p or "insurance certificate" in p or ("onboarded" in p and "missing" in p):
                response = (
                    "12 vendors onboarded in 2026 missing W-9 or insurance certificates:\n"
                    "  • 7 missing current W-9 (latest on file > 12 months)\n"
                    "  • 4 missing general liability COI ($2M minimum)\n"
                    "  • 3 missing workers-comp certificate (TX & LA work)\n"
                    "  • 2 with both W-9 and COI gaps (PIPETECH SVCS LLC, Apex Survey Group)\n"
                    "Combined non-PO spend exposure: $487,400. Auto-blocked from new payments. "
                    "Routed to vendor_compliance queue, SLA 10 business days."
                )
            elif "indemnity" in p or ("expired" in p and "clause" in p):
                response = (
                    "4 vendors with expired indemnity clauses on their active MSA:\n"
                    "  • ChemTreat · MSA-CHM-2023-08 · indemnity rider lapsed 2026-03-31 · $84K YTD spend\n"
                    "  • Archrock Services · MSA-ARC-2024-02 · indemnity sunset 2026-04-15 · $128K YTD\n"
                    "  • Exterran Corp · MSA-EXT-2023-11 · indemnity expired 2026-02-28 · $312K YTD\n"
                    "  • Coastal Crane Rentals · MSA-CCR-2024-06 · indemnity never executed · $42K YTD\n"
                    "Combined exposure: $566,400 of unprotected spend. Routed to legal_review queue, SLA 5 days."
                )
            elif "$1m" in p or "1m" in p or "year-to-date" in p or "ytd" in p or ("over" in p and "spend" in p):
                response = (
                    "Vendors with >$1M non-PO spend YTD 2026:\n"
                    "  • Exterran Corp · $2.14M · compressor PM (MSA-EXT-2023-11)\n"
                    "  • Emerson Process · $1.84M · instrumentation services (MSA-EMR-2024-09)\n"
                    "  • ChemTreat · $1.42M · water treatment chemicals (MSA-CHM-2023-08)\n"
                    "  • Archrock Services · $1.18M · gas-lift compression (MSA-ARC-2024-02)\n"
                    "Combined: $6.58M (47.2% of total non-PO spend). All 4 MSAs active and validated. "
                    "Recommend converting Exterran + Emerson to blanket POs for Q3."
                )
            elif "baker hughes" in p or "msa-bh-2025-11" in p or "tulsa" in p or "downhole" in p:
                response = (
                    "Validation: MSA-BH-2025-11 (Baker Hughes) for downhole NDT services in Tulsa region:\n"
                    "  • Scope Schedule B includes: ultrasonic, MFL, EMAT downhole inspection\n"
                    "  • Geographic coverage: TX, OK, NM, LA (Tulsa OK ✓ covered)\n"
                    "  • Rate-card valid through 2026-11-30 · indemnity active · COI on file\n"
                    "  • Confirmed: 3 Tulsa-region NDT invoices YTD ($142,800) auto-approved against this MSA\n"
                    "MSA-BH-2025-11 IS the correct contractual basis for the requested scope."
                )
            elif "mont belvieu" in p or "coi" in p or ("texas" in p and "qualified" in p):
                response = (
                    "5 vendors invoicing into Mont Belvieu cost centers (EPD-PROC-MTB-21, EPD-PL-MB-04) "
                    "without a Texas-qualified COI on file:\n"
                    "  • Coastal Crane Rentals · $42,400 · COI is LA-only\n"
                    "  • Gulf NDT Services · $15,200 · no COI uploaded\n"
                    "  • Apex Survey Group · $21,200 · COI expired 2026-03-31\n"
                    "  • Lone Star Electrical · $28,800 · missing TX workers-comp endorsement\n"
                    "  • Triad Inspection · $48,200 · COI is in draft\n"
                    "Combined exposure: $155,800. Auto-flagged in HITL queue, payments held until cure."
                )
            elif "auto-renew" in p or "90 days" in p or ("renew" in p and "next" in p):
                response = (
                    "8 vendor MSAs auto-renewing in the next 90 days:\n"
                    "  • MSA-HAL-2024-03 (Halliburton) · renews 2026-07-15 · 49 days · $4.8M annual\n"
                    "  • MSA-SLB-2025-0112 (Schlumberger) · renews 2026-07-22 · 56 days · $3.2M annual\n"
                    "  • MSA-BHI-2025-01 (Baker Hughes) · renews 2026-08-04 · 69 days · $1.9M annual\n"
                    "  • MSA-KIEWIT-2024-07 (Kiewit) · renews 2026-08-18 · 83 days · $6.4M annual\n"
                    "  • 4 more smaller MSAs ($200K-$800K annual).\n"
                    "All have PPI-FG escalation clauses. Recommend procurement opens renegotiation window today."
                )
            elif "above-market" in p or "above market" in p or ("non-po" in p and "maintenance" in p):
                response = (
                    "3 vendors charging above-market rates on non-PO maintenance work:\n"
                    "  • Archrock Services · gas-lift PM at $245/hr vs market $215/hr (+14.0%)\n"
                    "  • ChemTreat · field-tech callout at $185/hr vs market $162/hr (+14.2%)\n"
                    "  • Coastal Crane Rentals · 80-ton crane day-rate $4,200 vs market $3,650 (+15.1%)\n"
                    "Combined excess: $84,200 YTD. Recommend converting all 3 to PO with negotiated rate cards "
                    "before next month's spend cycle."
                )
            elif "q1" in p or "q2" in p or ("onboarding" in p and "compare" in p):
                response = (
                    "Onboarding compliance · Q1 2026 vs Q2 2026:\n"
                    "  • Q1: 23 new vendors · 91.3% complete on Day-1 (21/23) · avg cycle 4.2 days\n"
                    "  • Q2: 19 new vendors · 78.9% complete on Day-1 (15/19) · avg cycle 6.8 days\n"
                    "  • Q2 gaps: 3 missing COI, 2 missing W-9, 1 missing tax-exempt cert\n"
                    "  • Top Q2 friction: indemnity rider negotiations (avg +2.6 days)\n"
                    "Q2 compliance slipped 12.4 pts. Recommend standardizing the indemnity template to recover."
                )
            else:
                response = (
                    "VendorAgent processed 203 non-PO transactions in May 2026. "
                    "100% MSA coverage on validated transactions. 1 currently in HITL queue. "
                    "Ask me about a vendor (Exterran, Emerson, ChemTreat, Archrock), an MSA reference, "
                    "or May audit findings (0 this month)."
                )

        # ── QuoteAgent ──────────────────────────────────────────────────
        elif "quote" in agent_id:
            if ("fluor" in p and "historical" in p) or ("fluor" in p and "q2" in p):
                response = (
                    "Fluor Q2 quote QUOTE-FLUOR-2026-Q2-0142 vs historical engineering rates:\n"
                    "  • Senior process engineer:  $245/hr quoted vs $218/hr 12-mo avg  (+12.4%)\n"
                    "  • EPC project mgmt:        $185/hr quoted vs $172/hr 12-mo avg  (+7.6%)\n"
                    "  • Junior engineer:         $145/hr quoted vs $135/hr 12-mo avg  (+7.4%)\n\n"
                    "Blended scope is 9.5% above 12-mo average. Recommend procurement review before "
                    "issuing PO. Comparative report attached."
                )
            elif "validity" in p or ("open" in p and "beyond" in p):
                response = (
                    "6 engineering quotes open beyond their validity period:\n"
                    "  • QUOTE-BECHTEL-26-031 · $487K · expired 2026-05-12 (15 days stale)\n"
                    "  • QUOTE-FLUOR-2026-Q2-0142 · $284K · expired 2026-05-18 (9 days stale)\n"
                    "  • QUOTE-WORLEY-26-0072 · $218K · expired 2026-05-21 (6 days stale)\n"
                    "  • QUOTE-EMERSON-26-0418 · $142K · expired 2026-05-24 (3 days stale)\n"
                    "  • 2 more under $50K with similar lapses.\n"
                    "Combined value at risk: $1.18M. Recommend requesting fresh validity extensions today."
                )
            elif "bechtel-26-031" in p or ("bechtel" in p and "skid" in p) or ("bechtel" in p and "sweeny" in p):
                response = (
                    "Reconciliation: QUOTE-BECHTEL-26-031 vs executed PO-2026-EPC-7244 (Sweeny compressor skid):\n"
                    "  • Quoted: $487,000 lump-sum · PO issued: $487,000 lump-sum (100% match)\n"
                    "  • Quoted delivery: 14 weeks · PO milestone: 14 weeks (match)\n"
                    "  • Quoted scope (5 lines) reconciles 100% to PO Schedule B\n"
                    "  • One PO change-order: +$28,400 for upgraded ASME stamp (out-of-quote, approved)\n"
                    "Final PO value $515,400 · 5.8% above quote, all variance documented. CLEAN reconciliation."
                )
            elif "pipeline integrity" in p or "integrity studies" in p:
                response = (
                    "Quotes received this month for pipeline integrity studies — 4 active, $1.62M total:\n"
                    "  • QUOTE-BHI-26-INT-211 · Baker Hughes · $612K · ILI Mont Belvieu lateral (EPD-PL-MB-04)\n"
                    "  • QUOTE-SLB-26-INT-088 · Schlumberger · $487K · caliper run Seaway SE\n"
                    "  • QUOTE-QUEST-26-014 · Quest Integrity · $298K · MFL + ovality survey\n"
                    "  • QUOTE-HAL-26-INT-042 · Halliburton · $221K · cleaning pig + dewatering\n"
                    "Avg 12.4% above 12-mo benchmark — driven by Class-1 location density on Mont Belvieu route."
                )
            elif "kiewit" in p or "ppi-fg" in p or "escalation" in p:
                response = (
                    "Kiewit quotes with PPI-FG escalation clauses above 4%:\n"
                    "  • QUOTE-KIE-26-0418 · $1.84M · escalator PPI-FG +4.6% (cap exceeded by 0.6 pts)\n"
                    "  • QUOTE-KIE-26-0421 · $920K · escalator PPI-FG +4.2% (cap exceeded by 0.2 pts)\n"
                    "  • QUOTE-KIE-26-0438 · $487K · escalator PPI-FG +5.1% (cap exceeded by 1.1 pts)\n"
                    "MSA-KIEWIT-2024-07 caps escalation at 4.0%. Combined excess if approved: $94,200/year.\n"
                    "Routed to procurement HITL — recommend renegotiating to MSA-cap before PO issuance."
                )
            elif "$500k" in p or "500k" in p or "capital review" in p or "review board" in p:
                response = (
                    "Engineering quotes > $500K awaiting capital review board approval — 5 in queue:\n"
                    "  • QUOTE-BECHTEL-26-031 · $487K → bumped to $515K w/ ASME upgrade · Sweeny skid\n"
                    "  • QUOTE-BHI-26-INT-211 · $612K · Mont Belvieu ILI inspection\n"
                    "  • QUOTE-KIE-26-0418 · $1,840K · Sweeny compressor expansion (AFE-2024-0882)\n"
                    "  • QUOTE-FLR-26-0184 · $748K · Permian gathering FEED (AFE-2025-1104)\n"
                    "  • QUOTE-WORLEY-26-0091 · $584K · Midland tank-farm engineering (AFE-2026-0044)\n"
                    "Combined ask: $4.30M. CRB meets 2026-06-04. Recommend submitting full packages by 2026-05-30."
                )
            elif ("senior pe" in p or "senior process" in p) and ("compare" in p or "12 mo" in p or "12-mo" in p or "worley" in p):
                response = (
                    "Senior PE hourly rates — last 12 months across Fluor, Bechtel, Worley:\n"
                    "  • Fluor: 12 quotes · avg $232/hr · range $218-$245 · trend +5.2% YoY\n"
                    "  • Bechtel: 9 quotes · avg $227/hr · range $215-$240 · trend +3.8% YoY\n"
                    "  • Worley: 7 quotes · avg $218/hr · range $210-$232 · trend +2.4% YoY\n"
                    "Industry blended midpoint: $225/hr. Worley is most competitive but smallest sample size. "
                    "Recommend using $225/hr as the 2026 benchmark for senior PE work."
                )
            elif "scope-creep" in p or "scope creep" in p or "rejected" in p:
                response = (
                    "Quotes rejected for scope-creep flags in May 2026 — 3 of 47 (6.4% rejection rate):\n"
                    "  • QUOTE-EMR-26-0418 · scope added unbudgeted SIS upgrade (+$48K out of AFE)\n"
                    "  • QUOTE-EXT-26-0322 · scope added cold-weather package not in RFQ\n"
                    "  • QUOTE-FLR-26-0184 · scope added HAZOP facilitation outside MSA Schedule B\n"
                    "All 3 returned to vendor with revised RFQ. 2 re-quoted within 5 days. "
                    "May rejection rate trending down vs April (8.9%) — process improvements working."
                )
            elif "afe-2026-022" in p or "houston gathering" in p:
                response = (
                    "Quotes referencing AFE-2026-022 (Houston gathering expansion) — 4 active, $1.84M total:\n"
                    "  • QUOTE-KIE-26-0421 · Kiewit · $920K · pipe install + tie-ins\n"
                    "  • QUOTE-WORLEY-26-0072 · Worley · $218K · FEED + permitting\n"
                    "  • QUOTE-CAM-26-0188 · Cameron Int'l · $448K · valve packages + actuators\n"
                    "  • QUOTE-EMR-26-0322 · Emerson Process · $254K · SCADA + flow computers\n"
                    "AFE-2026-022 approved at $2.40M · current quoted commitment 76.7%. $560K headroom remaining."
                )
            elif "worley" in p or ("hot-tap" in p and "engineering" in p):
                response = (
                    "Validation: QUOTE-WORLEY-26-0072 vs MSA-WORLEY-2024-09 rate card (hot-tap engineering):\n"
                    "  • Senior PE: quoted $232/hr vs MSA $225/hr (+3.1%) — within 5% tolerance\n"
                    "  • Hot-tap specialist: quoted $268/hr vs MSA $258/hr (+3.9%) — within tolerance\n"
                    "  • CAD/redline: quoted $128/hr vs MSA $124/hr (+3.2%) — within tolerance\n"
                    "  • Mob/demob: quoted $8,400 lump-sum vs MSA $8,200 — within tolerance\n"
                    "Quote total $218K validates 100% to MSA. Auto-approved for PO conversion."
                )
            else:
                response = (
                    "QuoteAgent processed 47 engineering quotes in May 2026 at 88.4% accuracy. "
                    "1 in HITL queue (Exterran QUOTE-2026-0041, scope language ambiguous). "
                    "Avg decisioning: 2.1 days. Ask me about a specific vendor (Fluor, Bechtel, Emerson), "
                    "quote-vs-historical comparison, or open quotes past validity."
                )

        # ── TariffAgent ⭐ ──────────────────────────────────────────────
        elif "tariff" in agent_id:
            if ("effective" in p and ("may 27" in p or "may 27, 2026" in p or "today" in p)) or ("ngl tariff" in p and "effective" in p):
                response = (
                    "Effective FERC NGL tariff for May 27, 2026 (gas-day):\n"
                    "  • Enterprise NGL Pipeline LP (FERC-EPD-NGL-47.12.0): $0.180/bbl/100mi\n"
                    "  • Effective from 2025-07-01, next index cycle 2026-07-01 (35 days)\n"
                    "  • Projected next rate: $0.187/bbl/100mi (+3.6%) — PPI-FG driven\n"
                    "  • Annual revenue impact at projected rate: +$8.4M"
                )
            elif ("shipper" in p and ("above" in p or "billed" in p)) or "drift" in p or ("variance" in p and "rate" in p):
                response = (
                    "⚠ 23 shipper invoices billed above gas-day-effective FERC rate this month:\n"
                    "  • Texas Eastern (TETCO): $0.3012 billed vs $0.2847 FERC effective — 5.8% over\n"
                    "  • 312 affected shipper lines × avg 8,400 Dth/day × 30 days\n"
                    "  • Estimated overbilling exposure: $840,000/month if uncorrected\n\n"
                    "Routed to revenue team for FERC compliance review. HITL-high severity."
                )
            elif "next" in p and ("cycle" in p or "index" in p):
                response = (
                    "Next FERC index cycle: 2026-07-01 (35 days away).\n"
                    "PPI-FG index: 132.4 · YoY change: +3.61%\n"
                    "Projected blended rate change across 14 pipelines: +3.82%\n"
                    "Projected annual revenue uplift across portfolio: $51.2M"
                )
            elif "bbl/100" in p or "t-1" in p or "t-2" in p or "walk-up" in p or "mont belvieu lateral" in p:
                response = (
                    "Mont Belvieu lateral Bbl/100mi rates (FERC-EPD-NGL-47.12.0):\n"
                    "  • T-1 committed shippers (50K+ bpd):  $0.162/bbl/100mi (10% discount vs base)\n"
                    "  • T-2 committed shippers (15-50K bpd): $0.171/bbl/100mi (5% discount)\n"
                    "  • Walk-up uncommitted:                 $0.180/bbl/100mi (base)\n"
                    "Effective from 2025-07-01 · 14 T-1 shippers · 8 T-2 · 22 walk-up MTD. "
                    "Avg blended realization: $0.174/bbl/100mi against base."
                )
            elif "fuel adjustment" in p or "fuel adj" in p or ("ethane" in p and "tariff" in p) or ("rider" in p and "april" in p):
                response = (
                    "April 2026 ethane tariff fuel-adjustment rider validation (FERC-EPD-NGL-47.12.0):\n"
                    "  • Filed FAP: 2.18% of base rate (Mont Belvieu ethane lateral)\n"
                    "  • Power-cost basis: $0.0918/kWh weighted-average (April 2026)\n"
                    "  • Calculated FAP: 2.16% — filing within ±0.02% of computed value (OK)\n"
                    "  • Rider cap: 3.00% · current 2.18% well under cap\n"
                    "Validated — no exception. Filed correctly with FERC, applied to 14 shipper lines for April."
                )
            elif "ppi-fg" in p or ("pending" in p and "escalation" in p) or "quarter" in p:
                response = (
                    "Tariff sheets pending PPI-FG index escalation this quarter (Q2 2026):\n"
                    "  • FERC-EPD-NGL-47.12.0 (Enterprise NGL) · last reset 2025-07 · due 2026-07-01\n"
                    "  • FERC-EPD-CRUDE-22.4.0 (Seaway Crude) · last reset 2025-07 · due 2026-07-01\n"
                    "  • FERC-EPD-GAS-31.8.0 (Acadian Gas) · last reset 2025-07 · due 2026-07-01\n"
                    "  • FERC-EPD-NGL-AT-11.2.0 (Aransas Pass) · last reset 2025-07 · due 2026-07-01\n"
                    "  • FERC-EPD-CRUDE-SE-8.1.0 (Seaway SE) · last reset 2025-07 · due 2026-07-01\n"
                    "PPI-FG index +3.61% YoY → projected $51.2M annual revenue uplift across these 5 tariffs."
                )
            elif "propane" in p or ("july" in p and "current" in p) or "proposed" in p:
                response = (
                    "Proposed July 2026 propane tariff vs currently effective (FERC-EPD-NGL-47.12.0 propane):\n"
                    "  • Current effective (2025-07-01 base):  $0.182/bbl/100mi\n"
                    "  • Proposed July 2026 (PPI-FG indexed):  $0.189/bbl/100mi (+3.85%)\n"
                    "  • T-1 committed differential held flat at -10%\n"
                    "  • Annual revenue delta at projected throughput (32K bpd): +$2.6M\n"
                    "Notice period 60 days · FERC filing window opens 2026-06-01. On track for July 1 effective."
                )
            elif "wrong tariff" in p or "tariff revision" in p or ("wrong" in p and "revision" in p):
                response = (
                    "23 shipper invoices applied the wrong tariff revision in May 2026:\n"
                    "  • 14 invoices applied FERC-EPD-NGL-47.11.0 (superseded 2025-07-01) instead of 47.12.0\n"
                    "  • 6 invoices applied FERC-EPD-CRUDE-22.3.0 instead of 22.4.0 on Seaway Crude\n"
                    "  • 3 invoices applied an unfiled draft on Acadian Gas\n"
                    "  • Net rate variance: $0.0021/bbl avg · combined billing error $84,200\n"
                    "All flagged to revenue team for credit memo + re-bill. SLA 7 days, FERC compliance HITL-high."
                )
            elif ("flag" in p and "rider" in p) or ("rider cap" in p) or ("exceed" in p and "fuel" in p):
                response = (
                    "Tariff sheets where fuel-adjustment percentage exceeds the rider cap — 2 flagged:\n"
                    "  • FERC-EPD-GAS-31.8.0 (Acadian Gas) · filed FAP 3.42% vs cap 3.00% (over by 0.42 pts)\n"
                    "  • FERC-EPD-CRUDE-SE-8.1.0 (Seaway SE) · filed FAP 3.18% vs cap 3.00% (over by 0.18 pts)\n"
                    "Power-cost spike on the April 2026 ERCOT settle drove both. Net excess billing exposure: $148K.\n"
                    "Routed to FERC compliance HITL — recommend filing corrective notices within the 30-day window."
                )
            elif "docket" in p or ("filed" in p and "6 months" in p) or "past 6 months" in p:
                response = (
                    "FERC docket filings — past 6 months:\n"
                    "  • RP25-1188 · FERC-EPD-NGL-47.12.0 · Enterprise NGL Mont Belvieu · filed 2025-12-04\n"
                    "  • RP26-014 · FERC-EPD-CRUDE-22.4.0 · Seaway Crude · filed 2026-01-22\n"
                    "  • RP26-098 · FERC-EPD-GAS-31.8.0 · Acadian Gas index rate · filed 2026-02-18\n"
                    "  • RP26-142 · FERC-EPD-NGL-AT-11.2.0 · Aransas Pass propane · filed 2026-03-11\n"
                    "  • RP26-188 · FERC-EPD-CRUDE-SE-8.1.0 · Seaway SE extension · filed 2026-04-09\n"
                    "All 5 effective. 2 challenged at filing (RP25-1188, RP26-014) — both settled within 90 days."
                )
            else:
                response = (
                    "TariffAgent indexed 18 FERC pipelines · 312 tariff lines extracted in May 2026. "
                    "3 active rate-drift alerts (Texas Eastern, Panhandle Eastern, Trunkline LNG). "
                    "$840K revenue protected MTD. Ask me about effective gas-day rates, "
                    "FERC index forecasts, or shipper invoice drift."
                )

        # ── JIBAgent ⭐ ─────────────────────────────────────────────────
        elif "jib" in agent_id:
            if "partner share" in p and ("phillips" in p or "sweeny" in p or "april" in p):
                response = (
                    "EPROD partner share of April 2026 Sweeny Hub JIB:\n"
                    "  • Operator: Phillips 66 · JV: Sweeny Hub LLC · AFE-2024-0882\n"
                    "  • Gross JIB charge: $4,200,000 (capital + operating)\n"
                    "  • EPROD working-interest share: 50.00% → net $2,100,000\n\n"
                    "⚠ AFE balance check: $2.10M charged vs $1.85M approved remaining = $250K overrun.\n"
                    "Status: HITL-critical — escalated to Joint Venture Accounting."
                )
            elif ("targa" in p and "mont belvieu" in p and "capital" in p and ("exceed" in p or "afe-approved" in p)):
                response = (
                    "Targa Mont Belvieu JIB capital charges exceeding AFE-approved amounts (April 2026):\n"
                    "  • AFE-2025-0341 fractionation expansion: $4.62M JIB vs $4.20M AFE — $418K over\n"
                    "  • EPROD working-interest share: 50.00% → EPROD net overrun $209K\n\n"
                    "Combined Sweeny + Mont Belvieu overruns: $668K. Both routed to JV reconciliation "
                    "queue. Awaiting partner discussions before April closing."
                )
            elif "outside" in p or ("jv" in p and "scope" in p) or "agreement scope" in p:
                response = (
                    "JIB charges falling outside the JV agreement scope — 4 line items flagged:\n"
                    "  • JIB-PSX-SWEENY-26-04 · $48,200 · marketing & promo spend (not in JOA Schedule A)\n"
                    "  • JIB-TARGA-MTB-26-04 · $28,400 · partner G&A allocation > 8% (JOA caps at 6%)\n"
                    "  • JIB-PSX-SWEENY-26-04 · $14,800 · executive travel (excluded under JOA Article 7)\n"
                    "  • JIB-TARGA-MTB-26-04 · $9,600  · lobbying fees (excluded under JOA Article 7)\n"
                    "Combined disputed: $101,000. EPROD share at 50% WI: $50,500. Routed to JV Accounting dispute queue."
                )
            elif "reconcile" in p or "jib-psx-sweeny-26-04" in p or "afe-2026-008" in p:
                response = (
                    "Reconciliation: JIB-PSX-SWEENY-26-04 vs AFE-2026-008 (Sweeny fractionation expansion):\n"
                    "  • Line 1 · Compressor PM labor · JIB $284,200 · AFE budget $260K · +$24,200 over\n"
                    "  • Line 2 · Pipe & fittings · JIB $148,400 · AFE budget $160K · -$11,600 under\n"
                    "  • Line 3 · Operator allocated labor · JIB $84,800 · AFE budget $90K · -$5,200 under\n"
                    "  • Line 4 · Catalyst replacement · JIB $412,000 · AFE budget $380K · +$32,000 over\n"
                    "Net overrun: $39,400 on AFE-2026-008. EPROD share at 50% WI = $19,700. Routed to JV Accounting."
                )
            elif "working-interest" in p or "working interest" in p or ("split" in p and ("fractionation" in p or "jv" in p)):
                response = (
                    "Working-interest split — Sweeny fractionation JV (May 2026):\n"
                    "  • EPROD: 50.00% (operator pass-through partner)\n"
                    "  • Phillips 66: 35.00% (operator)\n"
                    "  • Targa Resources: 15.00% (carried interest)\n"
                    "JOA dated 2022-09-14 · Article 4 governs cost allocation · AFE-2026-008 in effect. "
                    "All May charges allocated per these splits — $4.84M gross → $2.42M EPROD net."
                )
            elif "backup" in p or ("invoice" in p and ("supporting" in p or "lack" in p)):
                response = (
                    "JIB line items lacking supporting vendor invoice backup — 7 entries:\n"
                    "  • JIB-PSX-SWEENY-26-04 · $84,200 · 'Maintenance services' — no invoice attached\n"
                    "  • JIB-TARGA-MTB-26-04 · $42,800 · 'Compressor parts' — invoice missing serial numbers\n"
                    "  • JIB-PSX-SWEENY-26-04 · $28,400 · 'Engineering oversight' — no timesheet detail\n"
                    "  • JIB-TARGA-MTB-26-04 · $18,200 · 'Operator labor' — wrong cost-center cited\n"
                    "  • 3 more under $10K with similar gaps.\n"
                    "Combined unbacked: $187,800. EPROD net (50% WI): $93,900. Pending partner upload, SLA 5 days."
                )
            elif "over-billed" in p or "over billed" in p or ("mont belvieu" in p and "joa" in p):
                response = (
                    "Partner over-billing to EPROD on Mont Belvieu JOA · YTD 2026:\n"
                    "  • Targa (operator) over-billed: $418K (AFE-2025-0341 capital overrun)\n"
                    "  • Phillips 66 (cross-JOA allocation): $148K (G&A pool > JOA cap)\n"
                    "  • Misc (vendor pass-through padding): $42K\n"
                    "Combined YTD over-billing: $608K · EPROD net at 50% WI = $304K disputed. "
                    "Currently in JV Accounting dispute queue, 2 partner-meeting cycles to close-out."
                )
            elif ("capital" in p and "operating" in p) or ("q1" in p and "q2" in p):
                response = (
                    "Targa JIB · Capital vs Operating charges · Q1 2026 vs Q2 2026:\n"
                    "  • Q1 Capital: $8.42M (AFE-2025-0341 ramp · 62% of gross JIB)\n"
                    "  • Q1 Operating: $5.18M (Mont Belvieu PM + chemicals)\n"
                    "  • Q2 Capital (April only): $4.62M (commissioning + tie-ins)\n"
                    "  • Q2 Operating (April only): $1.94M (running maintenance)\n"
                    "Q2 capital is tracking +9.7% over Q1 run-rate — driven by commissioning labor on EPD-PROC-MTB-21."
                )
            elif "partner share" in p and ("threshold" in p or "approval" in p or "exceed" in p):
                response = (
                    "JIB charges where partner share exceeds JOA-defined approval threshold (>$250K per line):\n"
                    "  • JIB-TARGA-MTB-26-04 · catalyst replacement · gross $412K · partner share $206K (>$200K JOA cap)\n"
                    "  • JIB-PSX-SWEENY-26-04 · fractionation skid · gross $487K · partner share $244K (under cap)\n"
                    "  • JIB-TARGA-MTB-26-04 · pipe & fittings replacement · gross $284K · partner share $142K\n"
                    "Only 1 over JOA-defined threshold. Routed to JV Accounting for partner countersignature, SLA 5 days."
                )
            elif "closed" in p or "fully spent" in p or ("afe" in p and ("flag" in p or "cite" in p)):
                response = (
                    "JIB entries citing AFEs that are closed or fully spent — 3 flagged this period:\n"
                    "  • JIB-PSX-SWEENY-26-04 · $48,200 → AFE-2024-0612 (closed 2026-02-28, fully spent)\n"
                    "  • JIB-TARGA-MTB-26-04 · $28,400 → AFE-2024-0744 (closed 2026-03-15, fully spent)\n"
                    "  • JIB-PSX-SWEENY-26-04 · $14,800 → AFE-2025-0188 (super-ceded by AFE-2025-0341)\n"
                    "Combined misallocation: $91,400. Recommend partner re-issue JIB against active AFE-2026-008. "
                    "Routed to JV Accounting with category=closed_afe_charge, SLA 7 days."
                )
            elif "afe" in p or "exceed" in p or "overrun" in p:
                response = (
                    "2 active JIB overrun flags this month:\n"
                    "  • Sweeny Hub JV · AFE-2024-0882: $2.1M charged vs $1.85M approved (+$250K)\n"
                    "  • Mont Belvieu JV · AFE-2025-0341: $4.62M charged vs $4.20M approved (+$418K)\n\n"
                    "Both routed to Joint Venture Accounting. 2 other AFEs ON TRACK (Permian +Midland). "
                    "Total AFE oversight: $21.55M approved · $21.49M charged · 4 JV partners."
                )
            else:
                response = (
                    "JIBAgent reconciled 28 JIB statements in May 2026 at 96.4% AFE match rate. "
                    "2 overruns currently active. 4 JV partners (Phillips 66, Targa, EPROD Operated × 2). "
                    "Ask me about a specific JV (Sweeny, Mont Belvieu, Permian, Midland), AFE (AFE-2024-0882), "
                    "or partner-share math."
                )
        else:
            response = (
                f"EPROD agent '{agent_id}' received: '{prompt[:60]}…'. "
                "I'm running in simulator-fallback mode (Foundry Agent Service cold-start exceeded 30s). "
                "The deployed runtime is READY in us-east-1; this is a temporary fallback that "
                "produces deterministic demo answers from the EPROD synthetic-data corpus."
            )

        return {
            "success":   True,
            "response":  response,
            "reasoning": [
                "Routed via EPROD simulator (Foundry Agent Service cold-start fallback)",
                "Inputs matched against EPROD synthetic-data heuristics",
            ],
            "actions_taken": ["simulator_lookup"],
            "agent_id":  agent_id,
            "source":    "eprod_simulator",
        }

    async def _invoke_runtime(
        self,
        agent_resource_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Invoke agent via AWS CLI - returns clean response only.

        When session_id is provided, it's forwarded to Foundry Agent Service as the
        runtime session id so the runtime's own server-side memory keeps
        multi-turn state even if the agent code itself is stateless.
        Foundry Agent Service requires the session id to be ≥33 chars, so we pad
        shorter ids with a deterministic suffix.

        `extra_payload` is merged into the JSON sent to the runtime; the
        STP agents read keys like `model_overrides` from there to switch
        their AzureOpenAIModel at tool-call vs synthesis time.
        """
        try:
            # Create temp file for response
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = f.name

            # Encode payload as base64. `extra_payload` (e.g. model_overrides)
            # is merged so STP agents can switch AzureOpenAIModel per call.
            payload_obj: Dict[str, Any] = {"prompt": prompt}
            if extra_payload:
                payload_obj.update(extra_payload)
            payload = json.dumps(payload_obj)
            payload_b64 = base64.b64encode(payload.encode()).decode()

            # Foundry Agent Service rejects session ids shorter than 33 chars. Pad with a
            # deterministic suffix so the same logical session still maps to
            # the same runtime session on the Foundry Agent Service side.
            cli_session_id: Optional[str] = None
            if session_id:
                cli_session_id = session_id
                if len(cli_session_id) < 33:
                    cli_session_id = f"{cli_session_id}-apex-session-pad"[:64]

            cmd = [
                "aws", "azure_openai-foundry_agent", "invoke-agent-runtime",
                "--agent-runtime-arn", agent_resource_id,
                "--region", self.region,
                "--payload", payload_b64,
            ]
            if cli_session_id:
                cmd += ["--runtime-session-id", cli_session_id]
            cmd.append(temp_file)

            # Invoke using AWS CLI (silent, no logs)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode == 0:
                # Read the response file
                with open(temp_file, 'r') as f:
                    response_data = json.load(f)

                # Clean up temp file
                os.unlink(temp_file)

                # Strands agents reply as {"result": {"role":"assistant","content":[{"text":"..."}]}}
                # Older bots may reply as {"response": "..."} — handle both.
                agent_response = self._extract_agent_text(response_data)
                reasoning, actions = self._extract_agent_reasoning(response_data)

                return {
                    "success": True,
                    "response": agent_response,
                    "reasoning": reasoning,
                    "actions_taken": actions,
                }
            else:
                os.unlink(temp_file)
                return {
                    "success": False,
                    "error": result.stderr or "AWS CLI invocation failed",
                    "response": None
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Agent invocation timed out",
                "response": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }

    def _invoke_cwfcu_simulator(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """Deterministic in-process simulator for the 5 CWFCU agents.

        Returns demo-quality answers anchored on the synthetic-data/cwfcu/
        corpus + the hand-off chain from the CWFCU story arc:

            Onboarding → Compliance → Loan Document → Vendor & Contract → Policy & HR

        Demo anchors used throughout: member #44821 (structuring SAR-0142),
        #39104 (EDD wire-to-3-countries), #29341 (CTR $12,400 cash deposit),
        Anderson (ONB-0200 PEP low-risk), Torres (ONB-0201 clean), Williams
        (re-upload), Patel LN-2026-0438 (mortgage $215K straight-through),
        Johnson LN-2026-0441 (HELOC $85K missing W-2), Fiserv (27d, $2.1M),
        Eltropy (41d), CO-OP, Diebold, Jack Henry. NCUA exam Jul 21, 2026
        (47d, 87% → 97%). FinCEN AML/CFT final rule, NCUA 2026 priorities.

        Each branch ends with the audit-lens line + downstream hand-off hint
        so the audience sees how the agents connect.
        """
        p = (prompt or "").lower()
        actions: list = []
        reasoning: list = []
        agent_label = "Compliance Agent"
        if "onboarding" in agent_id:
            agent_label = "Member Onboarding Agent"
        elif "loan" in agent_id:
            agent_label = "Loan Document Agent"
        elif "vendor" in agent_id:
            agent_label = "Vendor & Contract Agent"
        elif "policy" in agent_id:
            agent_label = "Policy & HR Agent"

        # ── MemberOnboardingAgent ───────────────────────────────────────
        if "onboarding" in agent_id:
            if "pending" in p or "this week" in p:
                response = (
                    "4 onboarding applications pending review this week:\n"
                    "  • ONB-2026-0200 · Anderson, P. · PEP hit (low-risk · Indiana state senator's spouse) · awaiting BSA Officer sign-off\n"
                    "  • ONB-2026-0201 · Torres, R. · OFAC clear · ID verified · ready to approve\n"
                    "  • ONB-2026-0202 · Williams, D. · ID document quality insufficient · re-upload sent via CWAnyWhere\n"
                    "  • ONB-2026-0203 · Park, J. · address verification mismatch (USPS DPV) · resolution in progress\n\n"
                    "Avg time-to-decision: 14 min. 3 ready for action.\n"
                    "[Audit Lens: queue snapshot logged] · → next, Compliance Agent will index Anderson into EDD watch."
                )
            elif "pep" in p:
                response = (
                    "PEP hits in the past 30 days — 2 members flagged:\n"
                    "  • ONB-2026-0200 · Anderson, P. · LOW-risk PEP (spouse of state senator)\n"
                    "    Source: WorldCheck One · Match score 92% · BSA Officer review queued\n"
                    "  • ONB-2026-0167 · Mendoza, C. · MEDIUM-risk PEP (former county commissioner)\n"
                    "    Source: Dow Jones RiskCenter · Match score 88% · EDD assigned to Compliance Agent\n\n"
                    "Both flow to Compliance Agent for ongoing CDD monitoring."
                )
            elif "average onboarding" in p or "onboarding time" in p:
                response = (
                    "Average onboarding time, June 2026: 11 min 42 sec (was 47 min manual baseline).\n"
                    "  • Median 9 min · p90 23 min · p99 38 min (PEP review path)\n"
                    "  • 204 members onboarded this month · 100% OFAC coverage\n"
                    "  • Straight-through rate: 78% · 22% routed to HITL\n\n"
                    "Bottleneck: PEP review (avg 6 min added). Investigating sub-second screening via WorldCheck API."
                )
            elif "address" in p and ("verification" in p or "failure" in p):
                response = (
                    "Address verification failures, May 2026 — 8 members:\n"
                    "  • 5 USPS DPV mismatch (typo / apt # missing) — auto-corrected, re-submitted\n"
                    "  • 2 PO Box only (account type doesn't allow PO Box per CWFCU policy P-OPS-114)\n"
                    "  • 1 multi-state address (member relocating between IN and MI)\n\n"
                    "All 8 routed back to applicant via CWAnyWhere with corrective guidance."
                )
            elif "ofac" in p and ("log" in p or "june" in p or "screening" in p):
                response = (
                    "OFAC screening log · June 2026 (through Jun 4):\n"
                    "  • 47 screenings performed · 100% completed within SLA (<3 sec)\n"
                    "  • 3 near-matches (>85% similarity) — all manually cleared by BSA Officer\n"
                    "    – Garcia, M. · 89% match (different DOB) · CLEARED\n"
                    "    – Singh, R. · 87% match (different country) · CLEARED\n"
                    "    – Khan, A. · 91% match (different middle initial) · CLEARED\n"
                    "  • 0 true matches · 0 accounts blocked\n\n"
                    "All cleared with documented rationale → indexed into NCUA exam folder."
                )
            elif "today" in p and "open" in p:
                response = (
                    "12 accounts opened today across all 4 branches:\n"
                    "  • Granger 4 · Mishawaka 3 · Elkhart 3 · South Bend 2\n"
                    "  • 10 share-savings · 2 share-draft (checking) added\n"
                    "  • All 12 cleared OFAC + PEP + CIP · 0 escalations\n\n"
                    "Total relationship value: $48,200 in opening deposits."
                )
            elif ("approve" in p and "onb-2026-0200" in p) or ("anderson" in p and "approve" in p):
                response = (
                    "Approving ONB-2026-0200 · Anderson, P. · LOW-risk PEP\n\n"
                    "  ✓ CIP packet complete (gov ID, SSN, DOB, address all verified)\n"
                    "  ✓ OFAC clear · PEP review attached (state senator's spouse, no sanctions risk)\n"
                    "  ✓ Beneficial ownership: N/A (consumer member)\n"
                    "  ✓ BSA Officer sign-off recorded · enhanced monitoring activated\n\n"
                    "Account approved · indexed into NCUA exam CIP folder.\n"
                    "→ next, Compliance Agent adds Anderson to EDD watch list per BSA program."
                )
            elif "torres" in p or "cip packet" in p:
                response = (
                    "CIP packet · Torres, R. · ONB-2026-0201:\n"
                    "  • Gov ID: Indiana DL #IN-3884-2719-09 — verified via AAMVA DLDV API (CLEAR)\n"
                    "  • SSN: validated against SSA SSNVS (issued 2003-MN, no death index hit)\n"
                    "  • Address: 1842 Main St, South Bend, IN 46613 — USPS DPV match (D1)\n"
                    "  • DOB: 1992-08-14 (verified, 33 yo · meets minimum-age policy)\n\n"
                    "OFAC screen: clear (3 near-matches dismissed by reviewer notes)\n"
                    "PEP screen: negative · Beneficial ownership: N/A (individual member)\n\n"
                    "All CIP requirements met. Ready for branch officer approval."
                )
            elif "re-upload" in p or "reupload" in p:
                response = (
                    "3 onboarding applications waiting on member re-upload:\n"
                    "  • Williams, D. — ID image too low-res (recommend 300 DPI minimum)\n"
                    "  • Park, J. — address proof expired (utility bill > 60d old)\n"
                    "  • Nguyen, T. — second ID document missing (CIP policy requires 2 forms)\n\n"
                    "All notified via CWAnyWhere app + email. Auto-reminder in 48 hrs if no upload."
                )
            elif "risk distribution" in p or ("low" in p and "medium" in p and "high" in p):
                response = (
                    "This week's new-member risk distribution (n=68):\n"
                    "  • LOW risk:    52 members (76%) — standard CIP, no EDD\n"
                    "  • MEDIUM risk: 14 members (21%) — high-cash-handling occupations, periodic CDD\n"
                    "  • HIGH risk:    2 members  (3%) — PEP flag + foreign nexus, EDD assigned\n\n"
                    "All HIGH-risk profiles handed off to Compliance Agent for enhanced monitoring."
                )
            else:
                response = (
                    f"{agent_label} (CW FCU) ready. I can pull pending onboardings, "
                    "show OFAC/PEP screening results, walk you through any CIP packet, "
                    "or summarize new-member risk distribution.\n\n"
                    "Sample queries: 'Show pending onboarding applications' · 'PEP flags this month' · "
                    "'Approve ONB-2026-0200' · 'CIP packet for Torres'."
                )

        # ── ComplianceAgent ─────────────────────────────────────────────
        elif "compliance" in agent_id:
            if "exam readiness" in p or "readiness score" in p:
                response = (
                    "NCUA exam readiness — June 4, 2026:\n\n"
                    "  Overall:                  87%  (target 97% by Jul 21)\n"
                    "  • BSA/AML Program Docs:   96%\n"
                    "  • Loan Underwriting:      91%\n"
                    "  • Member CDD Records:     88%\n"
                    "  • Vendor Risk Docs:       82%\n"
                    "  • Board Policy Acks:      74% ← drag — 22 of 84 staff overdue on BSA training\n\n"
                    "Exam window: Jul 21, 2026 · 47 days. At current trajectory APEX projects 97% by Jul 14.\n"
                    "→ I've handed the 22-employee gap to Policy & HR Agent for reminder follow-up."
                )
            elif "enhanced due diligence" in p or "edd flag" in p or ("members" in p and "flag" in p):
                response = (
                    "Members on EDD watch (n=18 active):\n"
                    "  • 6 high-cash-handling occupations (construction GCs, restaurant owners)\n"
                    "  • 4 PEP-related (incl. Anderson, P. — ONB-2026-0200)\n"
                    "  • 3 foreign-nexus (wire activity to 2+ countries)\n"
                    "  • 3 prior SAR subjects (incl. #44821 — current SAR-0142)\n"
                    "  • 2 NRA (non-resident alien) members\n\n"
                    "All have quarterly CDD refresh schedules · 4 due review this month."
                )
            elif "ctr" in p and ("pending" in p or "week" in p):
                response = (
                    "CTRs pending filing this week (3):\n"
                    "  • CTR-2026-05-1187 · Member #29341 · $12,400 cash deposit · 5/29 · filing window closes Jun 13\n"
                    "  • CTR-2026-05-1188 · Member #08812 · $15,000 wire-in   · 5/30 · auto-drafted, awaiting officer review\n"
                    "  • CTR-2026-05-1189 · Member #44123 · $10,500 cash deposit · 6/01 · auto-drafted\n\n"
                    "Year-to-date: 47 CTRs filed · 0 missed · 100% within 15-day window."
                )
            elif "bsa" in p and "training" in p:
                response = (
                    "BSA/AML training completion · CWFCU 2026:\n"
                    "  • 62 of 84 employees complete (74%)\n"
                    "  • 22 overdue — NCUA exam compliance requirement\n"
                    "  • 18 of the 22 are branch tellers (highest-risk role)\n"
                    "  • Avg time to complete: 47 min · deadline was May 31, 2026\n\n"
                    "→ Policy & HR Agent sent 2 reminder rounds; escalation to dept managers due Jun 10.\n"
                    "All 22 must complete before NCUA exam window opens (Jul 21)."
                )
            elif "cdd" in p and ("missing" in p or "annual review" in p):
                response = (
                    "14 CDD records flagged missing annual review:\n"
                    "  • 3 HIGH-risk members: #44821 (current SAR), #39104 (wire-to-3-countries), #61104\n"
                    "  • 8 MEDIUM-risk members\n"
                    "  • 3 LOW-risk members (overdue >18 mo)\n\n"
                    "All 14 routed to Compliance Officer with pre-filled review templates.\n"
                    "Avg review time: 12 min. Should clear all 14 well before Jul 21 exam."
                )
            elif "documents" in p and "missing" in p and "exam" in p:
                response = (
                    "NCUA exam folder gap analysis — 3 categories still need manual input:\n"
                    "  1. Updated BSA/AML risk assessment (annual) — last revised Mar 2025\n"
                    "  2. Board minutes from Apr 18, 2026 meeting (vendor mgmt policy adoption)\n"
                    "  3. 22 staff BSA training completions (HR system has 62/84)\n\n"
                    "All other 47 exam-prep documents have been auto-assembled (94% of NCUA's standard exam request list)."
                )
            elif "44821" in p or "structuring" in p or "sar narrative" in p:
                response = (
                    "SAR Narrative Draft — Member #44821 · SAR-2026-0142:\n\n"
                    "  \"On or about May 12 through May 28, 2026, the subject, account holder #44821,\n"
                    "  conducted 7 cash deposits totaling $47,300 at CommunityWide FCU branches across\n"
                    "  South Bend, Mishawaka, Elkhart, and Granger, Indiana. Individual transactions\n"
                    "  ranged from $5,800 to $8,900 — structured in amounts to avoid the $10,000\n"
                    "  Currency Transaction Report (CTR) filing threshold under 31 U.S.C. § 5313.\n"
                    "  Transaction pattern is consistent with structuring as defined under 31 U.S.C.\n"
                    "  § 5324. The subject's occupation (independent contractor) has no apparent\n"
                    "  business justification for the geographic and temporal distribution observed.\n"
                    "  CommunityWide FCU's BSA Officer has reviewed the activity and determined it\n"
                    "  warrants filing of this Suspicious Activity Report.\"\n\n"
                    "  Confidence: 96.1% · Ready for BSA Officer Review.\n"
                    "  [Audit Lens: narrative generated, logged]"
                )
            elif "sar" in p and ("open" in p or "30 days" in p or "past 30" in p):
                response = (
                    "Open SAR reviews — last 30 days (5 cases):\n\n"
                    "  SAR-0142 · #44821 · Structuring     · $47,300 · HIGH   · Pending BSA review\n"
                    "  SAR-0141 · #51887 · Layering        · $31,200 · HIGH   · Pending BSA review\n"
                    "  SAR-0138 · #38204 · Unusual wire    · $18,500 · MEDIUM · Filed Jun 1\n"
                    "  SAR-0135 · #29341 · Rapid movement  · $22,100 · MEDIUM · Filed May 28\n"
                    "  SAR-0131 · #17823 · Structuring     · $14,800 · LOW    · Filed May 15\n\n"
                    "2 open reviews require BSA Officer sign-off before the NCUA exam window opens.\n"
                    "[Audit Lens: decision logged]"
                )
            elif "ctr" in p and ("may" in p or "filings" in p):
                response = (
                    "CTR filings · May 2026 (12 filings):\n"
                    "  • 9 cash deposits ($10,000–$24,500) · all filed within 15-day window\n"
                    "  • 2 wire transactions ($18,200 + $22,400)\n"
                    "  • 1 cash withdrawal ($14,800)\n\n"
                    "Average filing latency: 4.2 days (target ≤ 15) · 0 missed · 0 amended.\n"
                    "All 12 indexed into NCUA exam BSA/AML folder."
                )
            else:
                response = (
                    f"{agent_label} (CW FCU) ready. I monitor BSA/AML, draft FinCEN-compliant SAR "
                    "narratives, file CTRs, run CDD reviews, and continuously assemble the NCUA exam "
                    "BSA/AML folder.\n\n"
                    "Sample queries: 'NCUA exam readiness score' · 'Open SAR reviews' · "
                    "'Draft SAR for #44821' · 'CDD records missing review' · 'BSA training status'."
                )

        # ── LoanDocumentAgent ───────────────────────────────────────────
        elif "loan" in agent_id:
            if "missing documents" in p or "missing docs" in p:
                response = (
                    "Loans in HITL queue with missing documents (4 packets):\n"
                    "  • LN-2026-0441 · Johnson, M. · HELOC $85K  · Missing 2024 W-2 · member notified\n"
                    "  • LN-2026-0443 · Patel, A.   · Mortgage $215K · Missing 2025 paystub · resolved\n"
                    "  • LN-2026-0448 · Williams, D. · Personal $12.5K · Income verification 62%\n"
                    "  • LN-2026-0451 · Nguyen, T.  · Auto $24.5K · Missing insurance binder\n\n"
                    "All notifications auto-sent via CWAnyWhere. Avg member response: 2.4 days."
                )
            elif "doc-to-decision" in p or "average" in p and ("decision" in p or "doc" in p):
                response = (
                    "Doc-to-decision time · June 2026 month-to-date:\n"
                    "  • Average: 1.4 days (down from 6.2 days manual baseline · -77%)\n"
                    "  • Median: 18 hrs · p90 3.1 days · p99 5.4 days\n"
                    "  • 93.8% straight-through (no HITL touch) · 6.2% HITL routed\n\n"
                    "Avg time savings per packet: ≈22 staff hrs. ROI vs manual: 4.4×."
                )
            elif "income verification failed" in p or "income" in p and "failed" in p:
                response = (
                    "Loans flagged for income verification failure this month (6):\n"
                    "  • 3 self-employed members — Schedule C inconsistencies vs deposits\n"
                    "  • 2 W-2 mismatch (employer name on paystub ≠ tax return employer)\n"
                    "  • 1 stale documentation (most recent paystub > 60 days)\n\n"
                    "All 6 routed to underwriter w/ specific remediation checklist."
                )
            elif "exception rate" in p:
                response = (
                    "Loan exception rate by type · June 2026 MTD:\n"
                    "  • HELOC:    13% exception rate ← highest (income complexity)\n"
                    "  • Mortgage:  9% (appraisal/title timing)\n"
                    "  • Personal:  6%\n"
                    "  • Auto:      2% ← lowest (most standardized packets)\n\n"
                    "Overall exception rate trending down 4 pts vs May 2026."
                )
            elif "expired id" in p or "id document" in p:
                response = (
                    "Active applications with expired ID documents (3):\n"
                    "  • LN-2026-0454 · Garcia, L. · DL expired Apr 2026 — re-upload requested\n"
                    "  • LN-2026-0461 · Chen, R.   · Passport expired Jan 2026 — alt ID accepted\n"
                    "  • LN-2026-0467 · Park, J.   · State ID expired May 2026 — re-upload requested\n\n"
                    "All 3 paused in HITL queue until re-upload."
                )
            elif "ln-2026-0441" in p or ("johnson" in p and ("checklist" in p or "underwriting" in p)):
                response = (
                    "Underwriting checklist · LN-2026-0441 · Johnson, M. · HELOC $85K:\n\n"
                    "  ✓ Loan application complete (CWAnyWhere submission)\n"
                    "  ✓ Property address verified · Granger, IN 46530\n"
                    "  ✓ Credit pull complete (FICO 742 · within policy band)\n"
                    "  ✓ 2025 paystubs (3 months) · income $94,200 ann\n"
                    "  ✗ 2024 W-2 MISSING  ← member notification sent 5/30, auto-reminder Jun 1\n"
                    "  ✓ Title search complete · no liens\n"
                    "  ☐ Appraisal scheduled Jun 10 (vendor: Heartland Valuation)\n\n"
                    "Packet 94% complete. Holding for W-2 receipt + appraisal."
                )
            elif "missing-w-2" in p or ("missing" in p and "w-2" in p and "johnson" in p):
                response = (
                    "Johnson packet · missing-W-2 walkthrough:\n"
                    "  1. Original CWAnyWhere submission included 2025 paystubs + 2024 tax return\n"
                    "  2. 2024 W-2 was not attached (tax return had Schedule 1 only)\n"
                    "  3. Loan Doc Agent auto-flagged on packet ingest (rule UW-104)\n"
                    "  4. Member notified via CWAnyWhere push + email at 14:22 on 5/30\n"
                    "  5. Auto-reminder fired 6/01 09:00 · still waiting\n\n"
                    "Escalation: if no upload by Jun 8, branch officer call follow-up.\n"
                    "Once received → straight-through to underwriter, projected close Jun 19."
                )
            elif "straight-through" in p or "auto loan" in p and "approval" in p:
                response = (
                    "Auto loan straight-through approval rate · May 2026: 96.1% (74 of 77 packets).\n"
                    "  • 3 HITL exceptions: 2 income verification, 1 dealer rebate variance\n"
                    "  • Avg straight-through time: 6.4 hrs (was 4.1 days manual)\n"
                    "  • Avg HITL time:           38.7 hrs\n\n"
                    "Best-performing loan type for automation."
                )
            elif "patel" in p or "ln-2026-0438" in p:
                response = (
                    "LN-2026-0438 · Patel, A. · Mortgage $215K · APPROVED:\n\n"
                    "  ✓ Full packet (32 documents) verified in 47 min\n"
                    "  ✓ FICO 782 · DTI 32% · LTV 78% (all within policy)\n"
                    "  ✓ Employment verified (Indiana University Health, 8 years)\n"
                    "  ✓ 2 yrs W-2 + 60d paystubs + bank statements\n"
                    "  ✓ Appraisal $278K · LTV met\n"
                    "  ✓ Title clear · HOI bound\n\n"
                    "Straight-through to underwriter Jun 1. Closed Jun 4. Total doc-to-decision: 3.1 days.\n"
                    "[Audit Lens: approval logged with full lineage]"
                )
            elif "extraction accuracy" in p or "compare loan packet" in p:
                response = (
                    "Loan packet extraction accuracy · June 2026 MTD:\n"
                    "  • Auto:     97.8% (most standardized forms)\n"
                    "  • Mortgage: 94.1% (Encompass LOS adapter)\n"
                    "  • HELOC:    91.4% (variable income docs)\n"
                    "  • Personal: 93.2%\n\n"
                    "Overall agent accuracy: 93.8% straight-through. Confidence floor: 0.85."
                )
            else:
                response = (
                    f"{agent_label} (CW FCU) ready. I extract every field from loan packets, "
                    "validate income docs, surface missing items, and route HITL items with "
                    "specific checklists.\n\n"
                    "Sample queries: 'Loans missing documents' · 'Doc-to-decision time' · "
                    "'Underwriting checklist for LN-2026-0441' · 'Auto loan straight-through rate'."
                )

        # ── VendorContractAgent ─────────────────────────────────────────
        elif "vendor" in agent_id:
            if "90 days" in p or "expire" in p:
                response = (
                    "Vendor contracts expiring in the next 90 days (4):\n"
                    "  • Fiserv Core Banking — Jul 1, 2026  (27 days) · $2.1M/yr · ⚠ AUTO-RENEWAL TODAY\n"
                    "  • Eltropy C-Dubs Chatbot — Jul 15, 2026 (41 days) · $180K/yr · negotiation open\n"
                    "  • Jack Henry Symitar feed — Sep 2, 2026 (89 days) · $96K/yr · standard renewal\n"
                    "  • Heartland Valuation — Sep 30, 2026 (118 days) · $142K/yr (over 90d but flagged)\n\n"
                    "Total contract value at risk: $2.5M annually."
                )
            elif "fiserv" in p and ("sla" in p or "performance" in p or "q2" in p):
                response = (
                    "Fiserv Core Banking · Q2 2026 SLA report:\n"
                    "  • Uptime:        99.97% (SLA: 99.95%) ✓\n"
                    "  • Response time: avg 142 ms (SLA: ≤200 ms) ✓\n"
                    "  • P1 incidents:  0 (SLA: ≤2/quarter) ✓\n"
                    "  • P2 incidents:  3 (SLA: ≤8/quarter) ✓\n"
                    "  • Support ticket avg: 2.4 hrs to first response (SLA: 4 hrs) ✓\n\n"
                    "Overall: zero SLA breaches Q2. Renewal recommendation: APPROVE w/ negotiated +1.8% rate cap."
                )
            elif "third-party risk" in p and "missing" in p:
                response = (
                    "Vendors missing third-party risk assessment (3):\n"
                    "  • Heartland Valuation Services (appraisal) — onboarded Mar 2026, no TPRM done\n"
                    "  • Indiana Title Co (title services) — assessment expired Feb 2026\n"
                    "  • Granger Insurance Agency — assessment never completed\n\n"
                    "All 3 routed to Compliance Officer for risk-based assessment.\n"
                    "→ NCUA exam will flag this — recommend completion before Jul 21."
                )
            elif "eltropy" in p and ("renewal" in p or "brief" in p):
                response = (
                    "Eltropy C-Dubs Chatbot · Renewal Brief\n\n"
                    "  Current term: Jul 15, 2024 → Jul 15, 2026 ($180K/yr)\n"
                    "  Proposed:     Jul 15, 2026 → Jul 15, 2028 ($192K/yr, +6.7%)\n"
                    "  Market comp:  Glia $215K · LivePerson $245K · Eltropy below market\n\n"
                    "  ✓ SLA performance: 99.94% uptime, 3 P2 incidents in past year\n"
                    "  ✓ Member engagement: 38% authentication digital, +14 pts YoY\n"
                    "  ⚠ Rate drift: +4.2% over baseline contract (above 3% drift threshold)\n"
                    "  ⚠ Policy obligation: data residency clause needs 2026 amendment\n\n"
                    "Recommendation: APPROVE w/ rate cap negotiation + data clause amendment."
                )
            elif "sla" in p and ("breach" in p or "month" in p):
                response = (
                    "Vendor SLA breaches · June 2026 MTD (2 minor):\n"
                    "  • CO-OP Shared Branch: 2 hr outage 6/02 (regional · IN/MI) — credited\n"
                    "  • Eltropy: chatbot response time 312ms 6/01 (SLA: ≤200ms · 38 min duration) — credit applied\n\n"
                    "No P1 vendor breaches. Both within contractual cure window."
                )
            elif "spend by category" in p or "total annual vendor" in p:
                response = (
                    "Annual vendor spend by category · 2026 trailing 12 months:\n"
                    "  • Core banking (Fiserv):        $2,100,000  (45%)\n"
                    "  • ATM / Shared branching:        $785,000  (17%) — Diebold + CO-OP\n"
                    "  • Member experience:             $324,000   (7%) — Eltropy + others\n"
                    "  • Compliance + audit:            $245,000   (5%)\n"
                    "  • Insurance + bonding:           $182,000   (4%)\n"
                    "  • Other (47 vendors total):    $1,058,000  (22%)\n\n"
                    "Total: $4.69M · -2.1% YoY (auto-negotiated cap savings)."
                )
            elif "fiserv" in p and ("delay" in p or "30 days" in p or "decision" in p or "renewal" in p):
                response = (
                    "Fiserv renewal decision · 30-day-delay impact analysis:\n\n"
                    "  If renewed today: $2.1M/yr × 2 years · rate locked at +2.4% vs current\n"
                    "  If delayed 30d:   auto-renewal kicks in at standard escalator (+5.8%)\n"
                    "                    Lost negotiation leverage → ≈$58K/yr higher cost\n"
                    "                    Member impact: nil (service continues)\n"
                    "                    NCUA exam: vendor mgmt finding likely (no TPRM refresh)\n\n"
                    "→ Recommend signing TODAY at negotiated rate.\n"
                    "  Triggers policy obligation chain to Policy & HR Agent (annual security training cert)."
                )
            elif "rate drift" in p or "escalation cap" in p:
                response = (
                    "Vendors with rate drift over contract escalation cap (3 alerts):\n"
                    "  • Fiserv:      +6.1% billed vs +3% cap → $58K/yr exposure ← high\n"
                    "  • Eltropy:     +4.2% billed vs +3% cap → $7.5K/yr exposure\n"
                    "  • Jack Henry:  +2.8% billed vs +3% cap → within tolerance\n\n"
                    "All 3 flagged for renewal-negotiation prep. Net YTD exposure: $96K."
                )
            elif "diebold" in p and ("sow" in p or "policy" in p or "obligation" in p):
                response = (
                    "Diebold ATM SOW · policy obligation chain:\n"
                    "  1. SOW §7.2 → all employees handling ATM cassette logistics must complete\n"
                    "     annual cash-handling training (CWFCU policy P-OPS-227)\n"
                    "  2. SOW §9.4 → quarterly key custodian acknowledgment refresh\n"
                    "  3. SOW §11.1 → annual third-party security training (incl. PCI)\n\n"
                    "→ Routed all 3 obligations to Policy & HR Agent for ack tracking.\n"
                    "Current status: 12 of 14 employees acknowledged P-OPS-227 · 2 overdue."
                )
            elif "co-op" in p and ("diebold" in p or "compare" in p or "shared branch" in p):
                response = (
                    "SLA performance YTD · CO-OP Shared Branch vs Diebold ATM:\n\n"
                    "  CO-OP:    Uptime 99.91% · Avg ticket 4.2 hrs · 1 critical (Jan 2026)\n"
                    "  Diebold:  Uptime 99.96% · Avg ticket 1.8 hrs · 0 critical\n\n"
                    "Diebold ahead on both metrics. CO-OP credit applied 6/02 (2 hr regional outage)."
                )
            else:
                response = (
                    f"{agent_label} (CW FCU) ready. I monitor 47 active vendor contracts for "
                    "expiry, SLA, rate drift, and renewal cycles. Critical alert: Fiserv "
                    "auto-renewal deadline is TODAY.\n\n"
                    "Sample queries: 'Contracts expiring next 90 days' · 'Fiserv SLA Q2' · "
                    "'Renewal brief for Eltropy' · 'Vendors missing TPRM'."
                )

        # ── PolicyHRAgent ────────────────────────────────────────────────
        else:
            if "bsa training" in p or ("haven't" in p and "completed" in p):
                response = (
                    "22 employees outstanding on BSA/AML training:\n"
                    "  • 18 branch tellers (highest-risk role · MUST complete before NCUA exam)\n"
                    "  •  2 loan officers\n"
                    "  •  1 collections specialist\n"
                    "  •  1 cybersecurity analyst (compliance overlap)\n\n"
                    "Auto-reminders: 2 rounds sent (May 31 + Jun 3) · escalation to dept managers Jun 10.\n"
                    "→ I've also flagged this on the NCUA exam readiness blocker list."
                )
            elif "acknowledgment" in p and ("department" in p or "completion" in p):
                response = (
                    "Policy acknowledgment completion by department:\n"
                    "  • Lending:        100% (12/12)\n"
                    "  • Operations:     100% (24/24)\n"
                    "  • Member Services: 96% (23/24)\n"
                    "  • IT / InfoSec:   100% (6/6)\n"
                    "  • Compliance:     100% (4/4)\n"
                    "  • Branch (tellers): 64% (9/14) ← needs follow-up\n\n"
                    "Overall: 78 of 84 employees current (92.9%) · 6 specific acks open."
                )
            elif "ncua exam readiness contribution" in p or "policy" in p and "contribution" in p:
                response = (
                    "Policy & HR contribution to NCUA exam readiness — 88% (target 95%):\n"
                    "  • Board policy acks:    74% (-13 to target — 6 specific acks open)\n"
                    "  • BSA/AML training:     74% (-13 to target — 22 employees overdue)\n"
                    "  • Annual board minutes: 92%\n"
                    "  • Personnel files:     100%\n"
                    "  • Code of conduct:     100%\n"
                    "  • Training records:     91%\n\n"
                    "I own the final 13 points of the exam readiness score."
                )
            elif "board resolution" in p and "signature" in p:
                response = (
                    "Board resolutions missing signatures (past 90 days · 3):\n"
                    "  • BOARD-RES-2026-04 · Vendor Mgmt Policy · awaiting 2 of 7 board signatures\n"
                    "  • BOARD-RES-2026-03 · CLO Adoption        · all signatures received\n"
                    "  • BOARD-RES-2026-02 · BSA Officer Renewal · awaiting 1 of 7 board signatures\n\n"
                    "2 outstanding resolutions block NCUA exam folder finalization.\n"
                    "Routed to Board Chair for execution at Jun 17 meeting."
                )
            elif "below 80" in p or ("policies" in p and "completion" in p):
                response = (
                    "Policies below 80% acknowledgment completion (3):\n"
                    "  • P-OPS-114 · Account Type Restrictions    · 74% (62/84)\n"
                    "  • P-COMP-201 · BSA/AML Updated Procedures  · 72% (60/84)\n"
                    "  • P-OPS-227 · Cash Handling Training        · 76% (64/84)\n\n"
                    "All 3 routed to dept managers for ack follow-up. NCUA exam attention items."
                )
            elif "hr audit summary" in p or ("audit" in p and "summary" in p):
                response = (
                    "HR audit summary · NCUA exam prep:\n\n"
                    "  Employee count:        84 (12 mo stable)\n"
                    "  Personnel files:       100% current\n"
                    "  Annual reviews 2025:   100% complete\n"
                    "  BSA/AML training:       74% (22 overdue — see remediation plan)\n"
                    "  Policy acks YTD:        93%\n"
                    "  Board policy adoption:  92%\n"
                    "  Code of conduct:       100%\n"
                    "  Whistleblower policy:  100% acked\n"
                    "  Insider trading:       100% acked\n\n"
                    "Single remediation item: 22 BSA training completions before Jul 21."
                )
            elif "send reminders" in p or "22 employees" in p:
                response = (
                    "Sending BSA training reminders to 22 overdue employees:\n"
                    "  • Email + CWFCU portal notification (auto-personalized)\n"
                    "  • SLA: complete within 7 days · escalation to dept mgr on Jun 11\n"
                    "  • Estimated completion projection: 18/22 by Jun 10, 22/22 by Jun 17\n\n"
                    "Reminder cycle 3 of 4 · final escalation goes to Margaret Rodriguez Jun 17.\n"
                    "[Audit Lens: notification batch logged]"
                )
            elif "board-res-2026-04" in p or "vendor management policy" in p:
                response = (
                    "BOARD-RES-2026-04 · Vendor Management Policy Adoption · ack status:\n\n"
                    "  Required signatories: 7 board members\n"
                    "  Received:             5 of 7\n"
                    "  Outstanding:          Director Sanjeev Patel · Director Elaine Whitmore\n\n"
                    "Both notified via DocuSign 5/22 · auto-reminders fired 5/29 + 6/01\n"
                    "Target signature deadline: Jun 17 board meeting · routed to Board Chair."
                )
            elif "vendor contract" in p and ("trigger" in p or "obligation" in p):
                response = (
                    "Policy obligations triggered by vendor contracts this quarter (4):\n"
                    "  • Fiserv renewal      → annual InfoSec training cert (94 employees affected)\n"
                    "  • Diebold ATM SOW     → annual cash-handling cert (14 cassette custodians)\n"
                    "  • Eltropy renewal     → data residency clause amendment (board action req)\n"
                    "  • Heartland Valuation → appraiser independence acknowledgment (12 lending staff)\n\n"
                    "All 4 added to policy ack queue. NCUA exam expects evidence."
                )
            elif "fincen" in p or "aml/cft" in p or "updated procedures" in p:
                response = (
                    "Employees who reviewed updated FinCEN AML/CFT procedures (60 of 84):\n"
                    "  • 60 completed acknowledgment of revised CWFCU BSA program (post-FinCEN rule)\n"
                    "  • 24 outstanding — overlap with the 22 BSA training overdue list (high correlation)\n\n"
                    "Effective date: Jul 1, 2026 · all 84 must ack before Jun 30.\n"
                    "→ Compliance Agent flagged this for the NCUA exam BSA/AML folder."
                )
            else:
                response = (
                    f"{agent_label} (CW FCU) ready. I track policy acknowledgments across 84 "
                    "employees, monitor BSA/AML training completion, manage board resolution "
                    "records, and own the final 13 points of the NCUA exam readiness score.\n\n"
                    "Sample queries: 'Employees overdue on BSA training' · 'Ack completion by dept' · "
                    "'Board resolutions missing signatures' · 'HR audit summary'."
                )

        actions.append({"name": "answer_drafted", "agent_id": agent_id, "ts": int(time.time())})
        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions,
        }

    def _invoke_boler_simulator(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """Deterministic in-process simulator for the 5 Boler agents.

        Anchors on synthetic-data/boler/ + the PDF brief:
          • 847 employees · 5 divisions (Hendrickson 412 · Real Estate 89 ·
            Holdings 124 · Mfg Services 156 · Corporate 66)
          • $2,142,000 total allocated · +3.2% vs May 2026
          • 4.2 hrs processing (was 3.5 days manual)
          • 7 exceptions: 2 HIGH (Chen R wrong-division, Martinez L duplicate
            COBRA), 3 MEDIUM, 2 LOW · $28,120 total variance
          • Stage 2 of 3 approval (Sarah Mitchell approved Stage 1 Jun 5,
            Ziggy Kravitz CFO Stage 2 pending Jun 6)
          • 4 active signals: Cigna +4.1% drift, 401k mismatch, Hendrickson
            growth, Step Functions SLA

        Every branch ends with the AWS architecture talking point or a
        downstream hand-off hint so the audience sees how the agents connect.
        """
        p = (prompt or "").lower()
        actions: list = []
        reasoning: list = []
        agent_label = "Benefits Allocation Agent"
        if "exception" in agent_id:
            agent_label = "Exception Resolution Agent"
        elif "je" in agent_id:
            agent_label = "Journal Entry Agent"
        elif "signal" in agent_id:
            agent_label = "Signal Agent"
        elif "audit" in agent_id:
            agent_label = "Audit Lens Agent"

        # ── BenefitsAllocationAgent (BEN) ───────────────────────────────
        if "benefits" in agent_id:
            if "high" in p and "exception" in p:
                response = (
                    "There are 2 HIGH exceptions in the June 2026 cycle requiring CFO action:\n\n"
                    "  EXC-0441 · Chen, Robert      · Wrong division — Hendrickson → Boler Holdings · $3,840/mo\n"
                    "  EXC-0442 · Martinez, Laura   · Duplicate COBRA + active enrollment              · $1,240/mo\n\n"
                    "Total HIGH variance: $5,080/month ($60,960 annualized if not corrected).\n"
                    "Both await your sign-off in the Human Review queue.\n"
                    "[Audit Lens: query logged to Cosmos DB] · → Exception Resolution Agent has prepared the reclassification."
                )
            elif "hendrickson" in p and "international" in p and ("last month" in p or "compare" in p):
                response = (
                    "Hendrickson International — June 2026 allocation breakdown:\n\n"
                    "  Benefit Type          May 2026       June 2026       Change\n"
                    "  Cigna Medical         $682,400       $710,800        +$28,400\n"
                    "  Delta Dental          $124,200       $126,800        +$2,600\n"
                    "  VSP Vision            $38,100        $38,200         +$100\n"
                    "  Fidelity 401k         $164,300       $167,000        +$2,700\n"
                    "  ──────────────────────────────────────────────────────────────\n"
                    "  Total                 $1,009,000     $1,042,800      +$33,800\n\n"
                    "The +$33,800 increase is primarily driven by Cigna medical rate change (+4.1% vs contracted rate). "
                    "APEX Signal has flagged this — Cigna renewal is in 41 days and no negotiation initiated. "
                    "Recommend escalating to Benefits Director before renewal auto-processes."
                )
            elif "hendrickson" in p and "cigna" in p and ("800" in p or "over" in p):
                response = (
                    "Hendrickson Intl employees with Cigna medical > $800/mo (47 employees · $44,820/mo total):\n\n"
                    "  • 12 employees with family-tier coverage   ($1,140-$1,240/mo)\n"
                    "  • 23 employees with EE+spouse coverage     ($820-$910/mo)\n"
                    "  • 12 senior staff with executive plans     ($1,380-$1,480/mo)\n\n"
                    "Highest single: Patel, A. · $1,480/mo (executive family · Hendrickson HQ).\n"
                    "Total Hendrickson Cigna spend June 2026: $710,800 · top 47 employees account for $44,820 (6.3%)."
                )
            elif "changed division" in p or "reallocation" in p:
                response = (
                    "4 employees changed divisions this cycle and need reallocation:\n\n"
                    "  EMP-4821 · Chen, Robert      · Hendrickson → Boler Holdings   · effective May 15 · $3,840/mo\n"
                    "  EMP-2241 · Kim, Susan        · Mfg Services → Real Estate     · effective May 22 · $1,920/mo\n"
                    "  EMP-3091 · Foster, Marcus    · Corporate → Hendrickson         · effective May 28 · $2,440/mo\n"
                    "  EMP-5184 · Reilly, Dana       · Boler Holdings → Mfg Services · effective May 30 · $1,920/mo\n\n"
                    "Total misallocation: $14,320/mo across 4 employees.\n"
                    "→ EMP-4821 (Chen) is the HIGH-priority EXC-0441 awaiting CFO. The other 3 were auto-fixed by APEX (EXC-0444)."
                )
            elif "journal entry" in p and "summary" in p:
                response = (
                    "Journal Entry Summary · All 5 Divisions · June 2026:\n\n"
                    "  Hendrickson Intl     $1,042,800     CC 6200-001\n"
                    "  Boler Holdings       $313,480       CC 6200-003\n"
                    "  Boler Mfg Services   $394,320       CC 6200-004\n"
                    "  Boler Real Estate    $224,910       CC 6200-002\n"
                    "  Corporate / Shared   $166,490       CC 6200-005\n"
                    "  ──────────────────────────────────────────────────\n"
                    "  Total                $2,142,000\n\n"
                    "→ JE Agent has generated all 5 JEs (DR/CR balanced). 3 are approved + ready for S3 distribution. "
                    "2 (Holdings, Mfg Services) still pending Stage 2 CFO approval."
                )
            elif "projected" in p and ("holdings" in p or "boler"  in p) and ("full-year" in p or "year" in p):
                response = (
                    "Projected full-year benefits cost · Boler Holdings 2026:\n\n"
                    "  H1 actual (Jan-Jun):       $1,812,180\n"
                    "  H2 projected (Jul-Dec):    $1,940,400 (based on current trajectory)\n"
                    "  Full-year projection:      $3,752,580\n"
                    "  Annual budget:             $3,612,000\n"
                    "  Projected variance:        +$140,580 (+3.9%)\n\n"
                    "Primary drivers:\n"
                    "  • Cigna medical rate drift (+4.1% over contract)\n"
                    "  • 6 new hires Q2 not yet in baseline (+$18,400/mo)\n"
                    "  • 401k match rate mismatch ($8,240/mo unresolved)\n\n"
                    "Recommend budget amendment + Cigna renewal negotiation before Q3."
                )
            elif "cigna rate card" in p or ("cigna" in p and "rate card" in p):
                response = (
                    "Cigna Rate Card vs Billed · June 2026:\n\n"
                    "                          Contract Rate   Billed Rate    Variance\n"
                    "  EE-only PPO             $612            $637            +4.1%\n"
                    "  EE + spouse PPO         $1,148           $1,195          +4.1%\n"
                    "  EE + child PPO          $1,012           $1,053          +4.1%\n"
                    "  Family PPO              $1,684           $1,753          +4.1%\n"
                    "  EE-only HDHP            $464            $483            +4.1%\n\n"
                    "Uniform +4.1% drift across all tiers. Total Cigna medical spend June: $1,284,320 · "
                    "$50,557 over contracted rate · annualized: $606,684 exposure if not negotiated.\n"
                    "→ Signal Agent flagged this 90 days ago. Renewal window opens in 41 days."
                )
            elif "over budget" in p and ("ytd" in p or "divisions" in p):
                response = (
                    "Divisions over budget YTD (through June 2026):\n\n"
                    "  Hendrickson Intl    +0.8% over   ($8,400 cumulative)        · within tolerance\n"
                    "  Boler Holdings      +4.1% over   ($12,520 cumulative)       ← Review · Cigna rate drift\n"
                    "  Boler Mfg Services  +1.4% over   ($5,520 cumulative)        · within tolerance\n"
                    "  Boler Real Estate   -1.2% under  ($2,730 surplus)           ✓ favorable\n"
                    "  Corporate           -0.3% under  ($510 surplus)              ✓ favorable\n\n"
                    "Net YTD variance: +$23,200 over budget across all 5 divisions.\n"
                    "Boler Holdings is the only division in the Review tier."
                )
            else:
                response = (
                    f"{agent_label} (Boler) ready. I have context on the June 2026 cycle: 847 employees, "
                    "5 divisions, 6 carrier files ($2.14M total), and 7 exceptions flagged.\n\n"
                    "Sample queries: 'Show HIGH exceptions with variance' · "
                    "'Hendrickson allocation vs last month' · 'Cigna rate card vs billed' · "
                    "'Generate JE summary for 5 divisions' · 'Divisions over budget YTD'."
                )

        # ── ExceptionResolutionAgent (EXC) ──────────────────────────────
        elif "exception" in agent_id:
            if "exc-2026-0441" in p or "exc-0441" in p or ("chen" in p and ("walk" in p or "exception" in p)):
                response = (
                    "EXC-2026-0441 · Wrong Division Reclassification · HIGH priority\n\n"
                    "Subject: Chen, Robert (EMP-4821)\n"
                    "Detected: Jun 6 09:41 by Benefits Allocation Agent\n"
                    "Source:   HRIS cross-reference vs carrier file allocation\n\n"
                    "Finding: Chen transferred from Hendrickson Intl to Boler Holdings on May 15, 2026.\n"
                    "All 6 benefit lines (Cigna medical, Delta dental, VSP vision, Fidelity 401k, Hartford life, "
                    "Cigna STD/LTD) are still allocated to Hendrickson Intl cost center 6200-001.\n\n"
                    "Total misallocation: $3,840/month ($46,080 annualized).\n\n"
                    "Recommended action:\n"
                    "  - Hendrickson Intl · Cost Center 6200-001 · $3,840/mo\n"
                    "  + Boler Holdings · Cost Center 6200-004 · $3,840/mo\n\n"
                    "Status: Awaiting CFO sign-off. Action buttons: [Apply Reclassification] [Override with Note]."
                )
            elif ("apply" in p or "reclassif" in p) and "chen" in p:
                response = (
                    "✓ Reclassification applied for Chen, Robert (EMP-4821):\n\n"
                    "  - Hendrickson Intl · CC 6200-001 · $3,840/mo · REMOVED\n"
                    "  + Boler Holdings   · CC 6200-004 · $3,840/mo · ADDED\n\n"
                    "Backdated to effective transfer date: May 15, 2026.\n"
                    "Catch-up adjustment: $1,920 prorate for May posted to Jun JE.\n\n"
                    "Audit ID: AUDIT-2026-06-06-09:41:03-EXC-0441-APPLIED\n"
                    "Audit Lens logged · Hendrickson + Boler Holdings JEs auto-updated.\n"
                    "→ JE Agent has regenerated both division JEs. Stage 2 approval can now proceed."
                )
            elif "exc-2026-0442" in p or "exc-0442" in p or "martinez" in p:
                response = (
                    "EXC-2026-0442 · Duplicate Enrollment · HIGH priority\n\n"
                    "Subject: Martinez, Laura (EMP-3312)\n"
                    "Detected: Jun 6 09:38 by Benefits Allocation Agent\n"
                    "Source:   Cigna medical file + Cigna COBRA file cross-reference\n\n"
                    "Finding: Martinez was terminated April 30, 2026. She appears in BOTH:\n"
                    "  • Active Cigna medical file ($1,240/mo charged to Boler Holdings)\n"
                    "  • Cigna COBRA billing file (self-pay continuation)\n\n"
                    "The $1,240/mo active charge is INVALID — terminated employees should not have active "
                    "corporate-allocated medical. COBRA is self-pay and should not hit corporate cost centers.\n\n"
                    "Recommended action:\n"
                    "  - Active Medical: $1,240/mo to Boler Holdings (INVALID)\n"
                    "  + COBRA is self-pay — remove from corporate allocation entirely\n\n"
                    "Status: Awaiting CFO sign-off. Action buttons: [Remove from Allocation] [Flag for HR Review]."
                )
            elif "awaiting" in p and ("cfo" in p or "variance" in p):
                response = (
                    "Exceptions awaiting CFO sign-off — 2 items, $5,080/mo total variance:\n\n"
                    "  EXC-2026-0441 · Chen, R.     · Wrong division reclassification · $3,840/mo\n"
                    "  EXC-2026-0442 · Martinez, L. · Duplicate Cigna medical + COBRA · $1,240/mo\n\n"
                    "Annualized exposure if not corrected: $60,960\n"
                    "Both exceptions are blocking Stage 2 distribution to division controllers.\n\n"
                    "→ Both routed via Step Functions to Ziggy Kravitz (CFO) at 09:38 Jun 6 · SES + SNS notifications sent.\n"
                    "SLA: 24 hours · current age 18 hours · approval due by 3pm today."
                )
            elif ("auto-fix" in p or "auto fix" in p) and "exception" in p:
                response = (
                    "Auto-fixed exceptions this cycle (no human review required) — 2 items:\n\n"
                    "  EXC-2026-0444 · Division transfer not reflected · 4 employees · $14,320/mo · AUTO-FIXED\n"
                    "                  (Kim, Foster, Reilly + 1 — auto-reclassified per HRIS source-of-truth)\n\n"
                    "  EXC-2026-0446 · Thompson, D. · Terminated May 28, vision + dental still billed · $420/mo · AUTO-FIXED\n"
                    "                  (Auto-termination cascade per HRIS termination date)\n\n"
                    "Auto-fix rate this cycle: 2 of 7 (29%) · all 2 require zero human touch.\n"
                    "→ All auto-fixes logged to Cosmos DB audit ledger with full lineage."
                )
            elif "sla" in p or "resolution time" in p:
                response = (
                    "HIGH-severity exception SLA: 24 hours from detection to disposition.\n\n"
                    "Current HIGH exceptions (June 2026):\n"
                    "  EXC-0441 · Chen, R.     · Detected 09:41 Jun 6 · Age 18h · 6h remaining\n"
                    "  EXC-0442 · Martinez, L. · Detected 09:38 Jun 6 · Age 18h · 6h remaining\n\n"
                    "Average HIGH resolution time YTD: 11.4 hours (well under 24h SLA).\n"
                    "Average MEDIUM resolution time:    2.8 days\n"
                    "Average LOW resolution time:        7.2 days\n\n"
                    "Step Functions enforces SLA via timer-based escalation. If 3pm passes without "
                    "CFO action, escalation cascades to COO via Teams + SES."
                )
            elif "401k" in p and ("mismatch" in p or "match rate" in p):
                response = (
                    "EXC-2026-0445 · 401k Match Rate Mismatch · MEDIUM priority\n\n"
                    "Subject: All 803 401k-enrolled employees\n"
                    "Detected: Jun 6 09:31 by Benefits Allocation Agent\n"
                    "Source:   Fidelity_401k_Jun2026.csv vs HR policy document\n\n"
                    "Finding: Fidelity carrier file shows employer match rate 4.5%. "
                    "Current HR policy P-COMP-401K-2024 specifies 4.0% match.\n\n"
                    "Financial impact: 0.5% delta × $1,648,000 eligible compensation × month = $8,240 monthly delta.\n"
                    "Year-to-date impact: $49,440 over policy.\n\n"
                    "Two possible resolutions:\n"
                    "  1. HR policy was updated to 4.5% but not propagated to allocation system\n"
                    "  2. Fidelity is using stale rate card — needs vendor correction\n\n"
                    "Status: Awaiting Benefits Director review (Sarah Mitchell).\n"
                    "→ Routed via Step Functions on Jun 6 at 09:31. Stage 1 action required."
                )
            elif "summary" in p and ("7 exception" in p or "all exception" in p or "cfo" in p):
                response = (
                    "Exception Summary · June 2026 Cycle · For CFO Sign-Off Package\n\n"
                    "  ID         Severity  Description                                    Variance     Status\n"
                    "  ─────────  ────────  ─────────────────────────────────────────────  ───────────  ────────\n"
                    "  EXC-0441   HIGH      Chen, R. wrong-division reclass               $3,840/mo    AWAITING CFO\n"
                    "  EXC-0442   HIGH      Martinez, L. duplicate Cigna + COBRA          $1,240/mo    AWAITING CFO\n"
                    "  EXC-0443   MEDIUM    Cigna rate change (+8.4% Boler Holdings)      $2,180/mo    Awaiting Benefits\n"
                    "  EXC-0444   MEDIUM    4 division transfers reclassified              $14,320/mo   AUTO-FIXED\n"
                    "  EXC-0445   MEDIUM    401k match rate mismatch (4.5% vs 4.0%)       $8,240/mo    Awaiting Benefits\n"
                    "  EXC-0446   LOW       Thompson, D. terminated benefits removed       $420/mo      AUTO-FIXED\n"
                    "  EXC-0447   LOW       3 new hires missing cost-center code            $6,840/mo    Awaiting Benefits\n"
                    "  ────────────────────────────────────────────────────────────────────────────────────────────────\n"
                    "                                                          TOTAL: $28,120/mo · 4 awaiting human action\n\n"
                    "PDF export ready for Sharepoint upload."
                )
            else:
                response = (
                    f"{agent_label} (Boler) ready. 7 exceptions in queue · 2 HIGH awaiting CFO · $28,120 total variance.\n\n"
                    "Sample queries: 'Walk me through EXC-0441 (Chen)' · 'Apply reclassification for Chen' · "
                    "'Duplicate enrollment case Martinez' · '401k mismatch' · 'Generate CFO summary'."
                )

        # ── JournalEntryAgent (JE) ──────────────────────────────────────
        elif "je" in agent_id:
            if "hendrickson" in p and ("generate" in p or "journal entry" in p):
                response = (
                    "Hendrickson Intl · Journal Entry · June 2026 · GL-coded\n\n"
                    "  DR 6200-001 · Benefits Expense — Medical          $624,480\n"
                    "  DR 6200-002 · Benefits Expense — Dental             $91,840\n"
                    "  DR 6200-003 · Benefits Expense — 401k Match        $201,760\n"
                    "  DR 6200-004 · Benefits Expense — Vision/Life/LTD   $124,720\n"
                    "    CR 2100-001 · Benefits Payable — Cigna                  $1,042,800\n\n"
                    "Balance check: DR $1,042,800 = CR $1,042,800 ✓\n"
                    "Period: June 2026\n"
                    "Posting date: Jun 7, 2026 (scheduled)\n"
                    "Distribution: S3 + SES to Hendrickson controller (Lisa Tanaka)\n"
                    "Audit ID: AUDIT-2026-06-07-08:00:00-JE-HEND-006\n\n"
                    "Status: Approved · awaiting Stage 3 distribution."
                )
            elif "preview" in p and ("5 division" in p or "all" in p):
                response = (
                    "JE Preview · All 5 Divisions · June 2026:\n\n"
                    "  Hendrickson Intl     DR $1,042,800   CR $1,042,800  ✓ BALANCED · Ready\n"
                    "  Boler Holdings       DR $313,480     CR $313,480    ✓ BALANCED · Pending CFO\n"
                    "  Boler Mfg Services   DR $394,320     CR $394,320    ✓ BALANCED · Pending CFO\n"
                    "  Boler Real Estate    DR $224,910     CR $224,910    ✓ BALANCED · Ready\n"
                    "  Corporate/Shared     DR $166,490     CR $166,490    ✓ BALANCED · Ready\n"
                    "  ──────────────────────────────────────────────────────────────────────────\n"
                    "  Total                DR $2,142,000   CR $2,142,000\n\n"
                    "3 of 5 ready for distribution · 2 (Holdings + Mfg Services) waiting on CFO sign-off for HIGH exceptions."
                )
            elif "approved" in p and "division" in p and "ready" in p:
                response = (
                    "Divisions with approved JEs ready for distribution:\n\n"
                    "  Hendrickson Intl    · Approved Jun 5 09:22 · Sarah Mitchell (Benefits Dir) + Ziggy Kravitz (CFO)\n"
                    "  Boler Real Estate   · Approved Jun 5 09:22 · Sarah Mitchell + Ziggy Kravitz\n"
                    "  Corporate/Shared    · Approved Jun 5 09:22 · Sarah Mitchell + Ziggy Kravitz\n\n"
                    "Distribution destination: S3 restricted bucket s3://boler-je-distribution/2026-06/\n"
                    "Notification: SES to division controllers + SNS to Power BI refresh job.\n"
                    "Scheduled: Jun 7 08:00 ET (auto-distribution via Step Functions).\n\n"
                    "Pending: Boler Holdings, Boler Mfg Services — both blocked on EXC-0441/0442 CFO sign-off."
                )
            elif "gl coding" in p or "gl-coding" in p or ("breakdown" in p and "holdings" in p):
                response = (
                    "Boler Holdings · GL Coding Breakdown · June 2026:\n\n"
                    "  DR 6200-003-001 · Medical (Cigna)              $198,400\n"
                    "  DR 6200-003-002 · Dental (Delta)                $39,600\n"
                    "  DR 6200-003-003 · 401k Match (Fidelity)         $63,000\n"
                    "  DR 6200-003-004 · Vision (VSP) + Life (Hartford) $12,480\n"
                    "    CR 2100-003 · Benefits Payable                 $313,480\n\n"
                    "Cost center: 6200-003\n"
                    "Allocation key: per-employee with division attribution from HRIS\n"
                    "Employees in this division: 124 (post-Chen reclassification: 125)\n"
                    "Per-employee average: $2,528/mo benefits cost."
                )
            elif "balance" in p and "hendrickson" in p:
                response = (
                    "Hendrickson Intl JE Balance Check:\n\n"
                    "  Total DR: $1,042,800\n"
                    "    DR 6200-001 Medical:     $624,480\n"
                    "    DR 6200-002 Dental:       $91,840\n"
                    "    DR 6200-003 401k Match:  $201,760\n"
                    "    DR 6200-004 Vision/LTD:  $124,720\n\n"
                    "  Total CR: $1,042,800\n"
                    "    CR 2100-001 Benefits Payable — Cigna: $1,042,800\n\n"
                    "  Balance: DR $1,042,800 = CR $1,042,800 ✓\n\n"
                    "Validation: JE Agent confirmed balance to penny precision before posting."
                )
            elif "cost-center" in p or "cost center" in p:
                response = (
                    "Cost-Center Breakdown · June 2026 · All 5 Divisions:\n\n"
                    "  6200-001 · Hendrickson Intl       · $1,042,800   (49% of total)\n"
                    "  6200-002 · Boler Real Estate      ·   $224,910   (10% of total)\n"
                    "  6200-003 · Boler Holdings          ·   $313,480   (15% of total)\n"
                    "  6200-004 · Boler Mfg Services      ·   $394,320   (18% of total)\n"
                    "  6200-005 · Corporate/Shared        ·   $166,490    (8% of total)\n"
                    "  ─────────────────────────────────────────────────────\n"
                    "                                       $2,142,000   (100%)\n\n"
                    "Each cost center is sub-coded by benefit type (medical, dental, 401k, vision/life/LTD)."
                )
            elif "distributed" in p or "controller" in p or "when" in p:
                response = (
                    "JE distribution schedule · June 2026:\n\n"
                    "  Scheduled date:  Jun 7, 2026 · 08:00 ET\n"
                    "  Mechanism:        Step Functions auto-distribution\n"
                    "  Destination:      s3://boler-je-distribution/2026-06/ (per-division restricted folder)\n"
                    "  Notifications:   SES (controllers) + SNS (Power BI refresh) + Teams channel\n"
                    "  Trigger:         Both HIGH exceptions resolved + Stage 2 CFO sign-off complete\n\n"
                    "Recipients:\n"
                    "  • Hendrickson Intl    → Lisa Tanaka, Division Controller\n"
                    "  • Boler Real Estate   → Marcus Brennan, RE Controller\n"
                    "  • Boler Holdings      → Diana Park, Holdings Controller\n"
                    "  • Boler Mfg Services  → Robert Ng, Mfg Controller\n"
                    "  • Corporate/Shared    → Sarah Mitchell, Benefits Director (interim)\n\n"
                    "Currently blocked: 2 HIGH exceptions awaiting CFO sign-off."
                )
            elif "csv" in p or "export" in p:
                response = (
                    "✓ CSV export generated · All 5 division JEs · June 2026\n\n"
                    "Filename: boler_je_export_2026-06.csv\n"
                    "Rows: 25 (5 divisions × 5 GL lines)\n"
                    "Size: 8.4 KB\n"
                    "Format: 8-column GL-friendly (Date, Division, CC, GL Account, Description, DR, CR, Audit ID)\n\n"
                    "Download URL: https://s3.amazonaws.com/boler-export/je_2026-06.csv (signed URL · 24hr TTL)\n"
                    "SES notification sent to Sarah Mitchell + Accounting team\n"
                    "Audit ID: AUDIT-2026-06-06-15:42:08-JE-EXPORT-001\n\n"
                    "→ All decisions and lineage immutably logged to Cosmos DB."
                )
            else:
                response = (
                    f"{agent_label} (Boler) ready. 5 division JEs generated · 3 approved + ready · "
                    "2 pending CFO sign-off.\n\n"
                    "Sample queries: 'Generate Hendrickson JE' · 'JE preview all 5 divisions' · "
                    "'GL coding for Holdings' · 'Confirm Hendrickson balance' · 'CSV export'."
                )

        # ── SignalAgent (SIG) ───────────────────────────────────────────
        elif "signal" in agent_id:
            if "cigna" in p and ("drift" in p or "90" in p):
                response = (
                    "Cigna Carrier Rate Drift · Trailing 90 Days:\n\n"
                    "  Month     Drift %    Status\n"
                    "  Jan 2026  +0.5%      ✓ within tolerance\n"
                    "  Feb 2026  +1.2%      ✓ within tolerance\n"
                    "  Mar 2026  +1.8%      ⚠ trending\n"
                    "  Apr 2026  +2.6%      ⚠ alert threshold (2.0%)\n"
                    "  May 2026  +3.4%      🚨 SIGNAL fired\n"
                    "  Jun 2026  +4.1%      🚨 active alert\n\n"
                    "Pattern: Linear escalation +0.6%/month. Forecast Jul +4.7%, Aug +5.3%.\n"
                    "Contract cap: +2.5% annual escalator. Current drift: +1.6 points OVER cap.\n\n"
                    "Annual exposure if not negotiated: $606,684 over contracted rate."
                )
            elif "cigna" in p and ("renew" in p or "negotia" in p):
                response = (
                    "Cigna Renewal Window · Negotiation Posture:\n\n"
                    "  Current term:        Apr 1, 2024 → Jul 31, 2026 (3-yr)\n"
                    "  Renewal window:      May 1 → Jul 1, 2026\n"
                    "  Auto-renewal:        YES — 24 months unless 30-day notice\n"
                    "  Notice deadline:     Jul 1, 2026 (41 days from today)\n\n"
                    "Current state:\n"
                    "  • Billed +4.1% over contract (+$50,557 over expected this month)\n"
                    "  • Annual exposure if not negotiated: $606,684\n"
                    "  • Cigna market alternative: BCBS Illinois quoted +2.4% (saves $230K/yr)\n\n"
                    "Leverage:\n"
                    "  ✓ 847-life book · attractive volume\n"
                    "  ✓ Documented rate drift breach\n"
                    "  ✓ Active alternate quote in hand\n\n"
                    "Recommend: Initiate renegotiation immediately. Target +2.0% (current cap + buffer)."
                )
            elif "division" in p and ("budget" in p or "variance" in p) and ("full year" in p or "forecast" in p or "2026" in p):
                response = (
                    "Division Budget Variance Forecast · Full Year 2026:\n\n"
                    "  Division              Annual Budget    Forecast        Variance\n"
                    "  Hendrickson Intl       $12,408,000      $12,668,640     +2.1% (+$260,640)\n"
                    "  Boler Holdings          $3,612,000       $3,752,580     +4.1% (+$140,580) ⚠\n"
                    "  Boler Mfg Services      $4,872,000       $4,784,640     -1.8% (-$87,360) ✓\n"
                    "  Boler Real Estate       $2,640,000       $2,648,520     +0.3% (within tolerance)\n"
                    "  Corporate/Shared        $2,004,000       $1,955,920     -2.4% (-$48,080) ✓\n"
                    "  ─────────────────────────────────────────────────────────────────────────\n"
                    "  Total                  $25,536,000      $25,810,300     +1.1% (+$274,300)\n\n"
                    "Boler Holdings is the only division above tolerance. Driven primarily by Cigna rate drift.\n"
                    "Model confidence: 89% · based on 18-mo trailing trend + carrier rate forecasts."
                )
            elif "open enrollment" in p or "november" in p or ("enrollment" in p and "forecast" in p):
                response = (
                    "Open Enrollment Impact Forecast · November 2026:\n\n"
                    "Current PPO enrollment: 761 employees\n"
                    "Projected HDHP migration: 62 employees (8.1% of PPO base)\n"
                    "Projected new dependents: 24 (Q3-Q4 new hires + qualifying events)\n\n"
                    "Annual cost impact:\n"
                    "  PPO → HDHP migration:        -$84,000/yr (lower premium tier)\n"
                    "  Dependent additions:          +$62,000/yr (new families enrolled)\n"
                    "  ──────────────────────────────────────────────────\n"
                    "  Net projected savings:        -$22,000/yr\n\n"
                    "Model confidence: 89% · based on 3-yr election trend + headcount projections\n"
                    "Key assumption: Cigna offers comparable HDHP for 2027 plan year (likely per contract)."
                )
            elif "above" in p and "contracted" in p and "rate" in p:
                response = (
                    "Carriers trending above contracted rate (June 2026):\n\n"
                    "  Cigna Medical      +4.1% drift   🚨 ALERT · renewal in 41d\n"
                    "  Delta Dental       +1.8% drift   ⚠ within +3% tolerance\n"
                    "  VSP Vision         +0.2% drift   ✓ within tolerance\n"
                    "  Fidelity 401k      -0.1%        ✓ at contracted match (4.0% per HR · BUT 4.5% billed → see EXC-0445)\n"
                    "  Hartford Life      +0.4% drift   ✓ within tolerance\n"
                    "  Cigna STD/LTD      +0.6% drift   ✓ within tolerance\n\n"
                    "Only Cigna Medical is in alert status. Total over-contract spend across all carriers: $58,797/mo."
                )
            elif "hendrickson" in p and ("headcount" in p or "growth" in p or "q3" in p):
                response = (
                    "Hendrickson Intl Headcount Growth Impact · Q3 2026 Forecast:\n\n"
                    "  Current Hendrickson headcount:    412 employees\n"
                    "  Q2 new hires (signed offers):     +12 employees (starting July)\n"
                    "  Q3 projected new hires:           +18 employees (per HR backfill plan)\n\n"
                    "Cost impact:\n"
                    "  Q3 incremental benefits cost:     +$18,400/mo (12 new hires fully enrolled)\n"
                    "  Q3 ramping cost:                  +$13,800/mo (18 partial enrollments)\n"
                    "  Total Q3 monthly delta:           +$32,200/mo (vs Q2 baseline)\n\n"
                    "Annualized impact: +$386,400 above current Q2 run-rate\n"
                    "Recommendation: Budget amendment for H2 — current Hendrickson budget has $0 for Q3 growth."
                )
            elif "401k" in p and "exposure" in p:
                response = (
                    "401k Match Rate Mismatch · Financial Exposure:\n\n"
                    "  Discrepancy:           Fidelity 4.5% vs HR policy 4.0%\n"
                    "  Eligible 401k base:    $1,648,000 monthly (803 enrolled employees)\n"
                    "  Delta:                  0.5% × $1,648,000 = $8,240/mo\n\n"
                    "Cumulative exposure:\n"
                    "  YTD (Jan-Jun):         $49,440\n"
                    "  Full-year if unresolved: $98,880\n"
                    "  3-yr cumulative:        $296,640\n\n"
                    "Root cause options:\n"
                    "  1. Fidelity rate card auto-incremented (typical 4.0% → 4.5% bump)\n"
                    "  2. HR policy was updated to 4.5% but not propagated to allocation system\n\n"
                    "Recommend: Sarah Mitchell (Benefits Director) confirm with Fidelity + HR within 7 days."
                )
            elif "signal brief" in p or "cfo" in p or ("4 active" in p and "signal" in p):
                response = (
                    "Signal Brief · For CFO · 4 Active Signals · June 6, 2026\n\n"
                    "ALERT (1):\n"
                    "  • Cigna Rate Drift +4.1% · Boler Holdings · Renewal in 41 days\n"
                    "    → Annual exposure $606,684 · negotiation window open · BCBS alternate quote -$230K\n\n"
                    "REVIEW (1):\n"
                    "  • 401k Match Rate Mismatch · Fidelity 4.5% vs HR 4.0%\n"
                    "    → $8,240/mo delta · root cause TBD · Sarah Mitchell follow-up requested\n\n"
                    "FORECAST (1):\n"
                    "  • Hendrickson Intl Headcount Growth · +12 Q2 + 18 Q3 new hires\n"
                    "    → +$32,200/mo by Q3 · budget amendment recommended\n\n"
                    "WATCH (1):\n"
                    "  • Step Functions SLA · Stage 2 CFO approval 18hr / 24hr SLA\n"
                    "    → 6 hours remaining · distribution delays if not actioned by 3pm today\n\n"
                    "Model confidence: 89% · last refreshed 2 minutes ago\n"
                    "Full Signal log available in Audit Lens tab."
                )
            else:
                response = (
                    f"{agent_label} (Boler) ready. 4 active signals · $28K variance caught · 3 forecasts live · "
                    "89% model confidence.\n\n"
                    "Sample queries: 'Cigna drift 90 days' · 'Cigna renewal posture' · "
                    "'Division budget variance forecast' · 'Open Enrollment forecast Nov 2026' · "
                    "'Generate Signal Brief for CFO'."
                )

        # ── AuditLensAgent (AUD) ────────────────────────────────────────
        else:
            if "audit trail" in p or ("full" in p and "trail" in p):
                response = (
                    "Audit Trail · June 2026 Cycle · The Boler Company · Cosmos DB\n\n"
                    "  09:14:22 · Jun 3 · 6 carrier files ingested from S3 intake bucket\n"
                    "                      847 employees · $2,142,000 total · APEX Benefits Agent\n"
                    "  11:32:07 · Jun 3 · APEX reclassification complete — 7 exceptions flagged\n"
                    "                      2 HIGH · 3 MEDIUM · 2 LOW · routed to Sarah Mitchell\n"
                    "  09:22:14 · Jun 5 · Stage 1 approved — Sarah Mitchell, Benefits Director\n"
                    "                      5 exceptions resolved · 2 overridden with notes\n"
                    "  09:18:33 · Jun 5 · Thompson, D. terminated employee removed\n"
                    "                      Vision + dental · $420 auto-fixed\n"
                    "  09:14:22 · Jun 5 · Division transfer reclassifications complete\n"
                    "                      4 employees · $14,320 auto-fixed (Kim, Foster, Reilly + 1)\n"
                    "  08:47:00 · Jun 6 · Stage 2 — Awaiting CFO review (Ziggy Kravitz)\n"
                    "                      JEs generated · 3 ready · 2 blocked on HIGH exceptions\n"
                    "  09:31:08 · Jun 6 · 401k match rate mismatch flagged · $8,240 delta\n"
                    "  09:35:14 · Jun 6 · Cigna rate drift alert generated · +4.1% above contract\n"
                    "  09:38:22 · Jun 6 · Stage 2 approval notification sent via SES + SNS to CFO\n"
                    "  09:41:03 · Jun 6 · EXC-0441 reclassification applied · $3,840 corrected\n\n"
                    "All entries immutably stored in Cosmos DB · KMS encrypted · 100% audit coverage."
                )
            elif "carrier file" in p and "ingest" in p:
                response = (
                    "Carrier File Ingest Audit · June 3, 2026 · S3 Intake Bucket\n\n"
                    "  09:14:22 · Cigna_Medical_Jun2026.csv      · 847 employees · $1,284,320 · INGESTED\n"
                    "  09:14:23 · Delta_Dental_Jun2026.csv       · 831 employees · $187,450    · INGESTED\n"
                    "  09:14:24 · Fidelity_401k_Jun2026.csv     · 803 employees · $412,880    · INGESTED\n"
                    "  09:14:24 · VSP_Vision_Jun2026.csv         · 798 employees · $62,140     · INGESTED\n"
                    "  09:14:25 · Hartford_Life_Jun2026.csv      · 847 employees · $98,760     · INGESTED\n"
                    "  09:14:26 · Cigna_STD_LTD_Jun2026.csv      · 847 employees · $94,450     · INGESTED\n\n"
                    "Total: 6 files · 847 unique employees · $2,142,000 total amount\n"
                    "Source: s3://boler-benefits-intake-restricted/2026-06/\n"
                    "Processing time: 4.2 hours (vs 3.5 days manual baseline)\n"
                    "All ingestion lineage stored in Cosmos DB with KMS-encrypted file hashes."
                )
            elif "stage 1" in p and ("approve" in p or "sarah" in p):
                response = (
                    "Stage 1 Approval Audit · June 5, 2026 · 09:22:14 ET\n\n"
                    "Approver:        Sarah Mitchell\n"
                    "Role:            Benefits Director\n"
                    "Method:          DocuSign + APEX approval portal\n"
                    "IP:              10.42.0.118 (Boler HQ corporate network)\n\n"
                    "Decisions:\n"
                    "  ✓ 5 exceptions RESOLVED   (auto-fix accepted)\n"
                    "  ✓ 2 exceptions OVERRIDDEN  (with documented notes)\n"
                    "       - EXC-0443 Cigna rate change: noted, awaiting carrier confirmation\n"
                    "       - EXC-0445 401k mismatch: noted, awaiting Fidelity vs HR resolution\n\n"
                    "Decision package routed to Stage 2 (Ziggy Kravitz, CFO) via:\n"
                    "  - SES email (timestamped + read-receipt confirmed)\n"
                    "  - SNS push notification\n"
                    "  - APEX approval portal queue entry\n\n"
                    "Audit ID: AUDIT-2026-06-05-09:22:14-STAGE1-APPROVED-MITCHELL"
                )
            elif "exc-0441" in p and "audit" in p:
                response = (
                    "Audit Entry · EXC-0441 Reclassification Applied · 09:41:03 Jun 6, 2026\n\n"
                    "Event:        EXC-2026-0441 reclassification applied\n"
                    "Subject:      Chen, Robert (EMP-4821)\n"
                    "Change:       Hendrickson Intl (CC 6200-001) → Boler Holdings (CC 6200-004)\n"
                    "Amount:       $3,840/mo (backdated to May 15 transfer effective date)\n"
                    "Catch-up:     $1,920 prorate for May posted to Jun JE\n\n"
                    "Approver:     Ziggy Kravitz (CFO) at 09:41 Jun 6\n"
                    "Approval ID:  STAGE2-APPROVAL-2026-06-06-EXC-0441\n\n"
                    "Downstream effects:\n"
                    "  ✓ Hendrickson JE regenerated (DR $1,038,960 → $1,042,800 after Chen subtracted)\n"
                    "  ✓ Boler Holdings JE regenerated (DR $309,640 → $313,480 after Chen added)\n"
                    "  ✓ HRIS allocation table updated\n"
                    "  ✓ Power BI dashboard auto-refresh queued for Jun 7 08:00\n\n"
                    "Audit ID: AUDIT-2026-06-06-09:41:03-EXC-0441-APPLIED\n"
                    "Storage: Cosmos DB (immutable) · KMS-encrypted · S3 backup hourly"
                )
            elif "coverage" in p:
                response = (
                    "Audit Coverage · June 2026 Cycle · The Boler Company:\n\n"
                    "  Employee records:    847 of 847    100% ✓\n"
                    "  Carrier files:        6 of 6        100% ✓\n"
                    "  Allocation decisions: 847 of 847    100% ✓\n"
                    "  Exception decisions:  7 of 7        100% ✓\n"
                    "  Approval stages:      3 of 3        100% ✓\n"
                    "  JE generations:       5 of 5        100% ✓\n"
                    "  ────────────────────────────────────────────\n"
                    "  Overall coverage:                    100% ✓\n\n"
                    "Storage: Azure Cosmos DB · KMS encrypted · cross-region replication\n"
                    "Retention: 7 years per Boler retention policy + SOC 2 requirement\n"
                    "Query latency: < 50ms for point lookups · < 200ms for cycle-wide queries\n\n"
                    "SOC 2 audit-ready: any examiner query answerable from immutable log."
                )
            elif "soc 2" in p or "soc2" in p or "export" in p:
                response = (
                    "SOC 2 Audit Export · June 2026 Cycle · Generated:\n\n"
                    "Package contents:\n"
                    "  • Full audit trail (JSON · 847 employee records × 6 carriers × 3 stages = 15,246 events)\n"
                    "  • Approval chain documentation (Stage 1 Sarah Mitchell, Stage 2 Ziggy Kravitz)\n"
                    "  • Exception resolution log (7 exceptions with disposition)\n"
                    "  • DR/CR balance proofs (5 divisions × $0 imbalance)\n"
                    "  • Cosmos DB lineage graph (PDF visualization)\n"
                    "  • KMS encryption proofs (key rotation log + access audit)\n"
                    "  • IAM role assumption log (no break-glass usage)\n\n"
                    "Package size: 42.8 MB\n"
                    "Format: ZIP + JSON manifest\n"
                    "Signed URL: https://s3.amazonaws.com/boler-soc2/2026-06-export.zip (72hr TTL)\n"
                    "Audit ID: AUDIT-2026-06-06-15:42:08-SOC2-EXPORT-001\n\n"
                    "SES notification sent to Boler Compliance Officer + external auditor."
                )
            elif "pending" in p and ("stage" in p or "age" in p):
                response = (
                    "Stage-2 Approval Pending Items · Currently 18 hours into 24hr SLA:\n\n"
                    "  JE-2026-0031 · Hendrickson Intl JE         · $1,042,800 · Age 18h · 6h remaining\n"
                    "  EXC-2026-0441 · Chen, R. reclassification   · $3,840/mo   · Age 18h · 6h remaining\n"
                    "  EXC-2026-0442 · Martinez duplicate enrollment · $1,240/mo · Age 18h · 6h remaining\n\n"
                    "SLA breach in 6 hours · escalation cascade to COO via Teams + SES if not actioned.\n"
                    "All items routed to Ziggy Kravitz (CFO) via Step Functions + SES + SNS.\n\n"
                    "Distribution delay impact if missed:\n"
                    "  • 5 division controllers receive JE files 24hr late\n"
                    "  • Power BI dashboard refresh delayed to Jun 8\n"
                    "  • Board reporting cycle pushed 1 business day\n"
                    "[Audit Lens: SLA-watch log refreshes every 60s]"
                )
            elif "lineage" in p and "cigna" in p:
                response = (
                    "Lineage Trace · Cigna Medical $1,284,320 · June 2026:\n\n"
                    "  Source:          s3://boler-benefits-intake-restricted/2026-06/Cigna_Medical_Jun2026.csv\n"
                    "  Ingest:           Jun 3 09:14:22 by Benefits Allocation Agent (Lambda + Azure OpenAI)\n"
                    "  File hash:       SHA-256 a4f8c2e1...d09b (cross-validated against carrier email)\n\n"
                    "Distribution across 5 divisions (per HRIS allocation):\n"
                    "  Hendrickson Intl     $710,800     (412 employees · 55.4%)\n"
                    "  Boler Mfg Services   $249,600     (156 employees · 19.4%)\n"
                    "  Boler Holdings       $198,400     (124 employees · 15.4%)\n"
                    "  Boler Real Estate    $63,440      (89 employees · 4.9%)\n"
                    "  Corporate/Shared     $62,080      (66 employees · 4.8%)\n"
                    "  ──────────────────────────────────────────────────────\n"
                    "  Total                $1,284,320   (847 employees · 100.0%)\n\n"
                    "Routing:          Sarah Mitchell (Stage 1) → Ziggy Kravitz (Stage 2 pending) → S3 distribution\n"
                    "Storage:           Cosmos DB · table=boler_lineage · partition=2026-06 · sort=cigna-medical\n"
                    "Query path:       Single-shot lookup · <50ms"
                )
            else:
                response = (
                    f"{agent_label} (Boler) ready. 100% audit coverage · 15,246 events logged this cycle · "
                    "Cosmos DB immutable · KMS-encrypted · SOC 2 audit-ready.\n\n"
                    "Sample queries: 'Full audit trail June 2026' · 'Carrier file ingest audit' · "
                    "'Stage 1 approval Sarah Mitchell' · 'Audit coverage percentage' · "
                    "'SOC 2 audit export' · 'Lineage Cigna $1,284,320'."
                )

        actions.append({"name": "answer_drafted", "agent_id": agent_id, "ts": int(time.time())})
        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions,
        }

    def _invoke_verizon_simulator(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """Deterministic in-process simulator for the 4 Verizon Far Edge agents.

        Anchored on James Patchett's REAL firmware corpus (118 reports in
        synthetic-data/verizon_far_edge/real_test_reports/):
          • Fleet: HPE Edgeline E910t/E920t/E930t (iLO5 3.06, iLO6 1.57/1.60/1.68),
            ZT Proteus/Triton/Galene (BMC .43/.45/.46, 2.31, 3.02, 1.13, CPLD),
            Dell PowerEdge R7615 (iDRAC 7.10.50.10). Wind River Cloud Platform
            (WRCP 21.05p6 → 21.12p10 → 22.12mr1), distributed-cloud subclouds.
          • HERO 1 — DMTF conformance triage: HPE iLO6 1.57 → PASS:392 FAIL:7.
            All 7 = WWW-Authenticate(6) + X.509-IPv6(1), known-benign, recur
            identically across the fleet. James: "marked test passed."
          • HERO 2 — Samsung PM9A3 thermal regression: BMC .45 can't read drive
            temp → fans spike to 100%; BMC .46 fixes it. Block .45 wave to
            PM9A3 sites.
          • Test catalog (real MEAKV IDs): 507 (DMTF), 508-517 (BIOS), 518-524
            (Monitoring/Sensor), 642-646 (PTU Perf), 648-655 (Redfish), 1789-1791
            (Sensor), 1792 (Samsung SSD), 1793 (BMC Playbook), 1860 (FlexRAN),
            965 (Platform Deploy), 239-241 (Platform System).
        """
        p = (prompt or "").lower()
        actions: list = []
        reasoning: list = []

        agent_label = "CertificationAgent"
        if "schema" in agent_id:
            agent_label = "SchemaWatchAgent"
        elif "upgrade" in agent_id:
            agent_label = "UpgradeAdvisorAgent"
        elif "mentor" in agent_id:
            agent_label = "MentorAgent"
        elif "orchestrat" in agent_id:
            agent_label = "OrchestratorAgent"
        elif "playbook" in agent_id:
            agent_label = "PlaybookAgent"

        response = None

        # ══════════ OrchestratorAgent (UC-0) — drives the end-to-end run ══════════
        if "orchestrat" in agent_id:
            if "tier" in p or ("read" in p and "action" in p) or "correlation vs" in p or "direct" in p:
                response = (
                    "Every step in the run is one of two tiers — this is the line your team cares about:\n\n"
                    "  ◇ REPORTING & CORRELATION (7 steps) — read-only intelligence. Detect blocked\n"
                    "    coverage, design test cases, pull real reference values from a live e930t,\n"
                    "    cross-platform correlation, gap analysis → change-spec, compliance scan.\n"
                    "    These MUTATE NOTHING in the lab.\n\n"
                    "  ⚡ DIRECT LAB ACTION (5 steps) — executes on live hardware: connect+baseline,\n"
                    "    run PROPOSED-20→28 ×5 iterations, apply playbook changes/open PR, PATCH BIOS +\n"
                    "    Secure Boot, re-certify ×5. EVERY direct action is gated by a human approval.\n\n"
                    "3 HITL gates in this run: authorize live execution · approve playbook changes ·\n"
                    "approve BIOS/secure-boot config. Nothing touches the lab without a human ✓."
                )
            elif "hitl" in p or "gate" in p or "approv" in p or "human" in p:
                response = (
                    "This run has 3 HITL gates — one before each class of lab mutation:\n\n"
                    "  Gate 1 · authorize live-lab execution (before running PROPOSED-20→28 on the unit)\n"
                    "  Gate 2 · approve the 7 Ansible playbook changes (before any commit/PR)\n"
                    "  Gate 3 · approve BIOS WorkloadProfile=vRAN + Secure Boot install (cold-boot cycle)\n\n"
                    "Read-only correlation/reporting steps run automatically — only direct lab actions stop\n"
                    "for a human. Every approval is hash-chained to the audit log with reviewer + timestamp."
                )
            elif "iteration" in p or "5 " in p or "five" in p or "run " in p or "20" in p:
                response = (
                    "PROPOSED-20→28 ran through 5 iterations on the live EL140 (iLO7):\n\n"
                    "  run1  9/9 pass · ilo-reset 133s\n"
                    "  run2  9/9 pass · 131s\n"
                    "  run3  8/9 · DNS 6-entry array → HTTP 400 ArrayPropertyOutOfBound (deviation found)\n"
                    "  run4  9/9 pass · DNS retried with 3-entry array [\"DNS1\",\"DNS2\",\"::\"]\n"
                    "  run5  9/9 pass · stable\n\n"
                    "Running 5× is what surfaced the iLO7 StaticNameServers 1..3 limit — a single run\n"
                    "would have missed it. That deviation became a required playbook change."
                )
            elif "dell" in p or "xr8720" in p:
                response = (
                    "Queuing Dell XR8720t (iDRAC 10 · BIOS 1.1.3 · Xeon 6776P-B GNR-D) next.\n"
                    "Same orchestration pattern: 40 tests, MEAKV inventory/sensor/BIOS + PROPOSED security.\n"
                    "Last campaign: 29 PASS · 10 PASS-WITH-DEVIATION · 1 PARTIAL · 0 FAIL.\n"
                    "Notable: IndicatorLED 'Off' → HTTP 400 on iDRAC 10 (Lit/Blinking only) — adapted."
                )
            elif "bob" in p or "summar" in p or "end-to-end" in p or "report" in p:
                response = (
                    "End-to-end run — HPE EL140 Gen12 onboarding:\n\n"
                    "  • A brand-new server type arrived; existing MEAKV tests + BMC playbook were BLOCKED.\n"
                    "  • 7 read-only correlation steps designed coverage, executed analysis, drafted the\n"
                    "    Ansible change-spec, and scanned compliance — touching nothing in the lab.\n"
                    "  • 5 direct lab actions ran the tests (×5 iterations), applied the approved playbook\n"
                    "    changes, and configured BIOS + Secure Boot — each behind a human approval.\n"
                    "  • Result: platform CERTIFIED, playbook PR ready, full audit trail.\n\n"
                    "Manual baseline ~40 hours of playbook archaeology → ~18 minutes orchestrated."
                )
            elif "time" in p or "40" in p or "hour" in p or "baseline" in p:
                response = (
                    "Manual baseline: onboarding a new server type = days of playbook archaeology + manual\n"
                    "Redfish probing — ~40 engineer-hours, and it stalls waiting on vendor MOPs.\n"
                    "Orchestrated: ~18 minutes wall-clock for the full design→execute→change-spec→re-cert\n"
                    "loop, with humans only in the approval gates. >95% reduction."
                )
            if response is None:
                response = (
                    "OrchestratorAgent ready. I drive the end-to-end certification run and keep two tiers\n"
                    "cleanly separated: read-only Reporting/Correlation (auto) vs Direct Lab Action (HITL-gated).\n\n"
                    "Try: 'Onboard the HPE EL140 Gen12' · 'Which steps are correlation vs direct action?' ·\n"
                    "'What did the 5 iterations find?' · 'Summarize the run for Bob.'"
                )

        # ══════════ PlaybookAgent (UC-5) — gap analysis → change-spec ══════════
        elif "playbook" in agent_id:
            if "how many" in p or "roles" in p or "7 " in p or "count" in p:
                response = (
                    "Gap analysis vs the live BMC playbook (commit 5ff15f7028) for HPE EL140 / iLO7:\n\n"
                    "  7 CHANGE REQUIRED · 7 NO CHANGE · 1 VERIFY REQUIRED · across 15 role files.\n\n"
                    "CHANGE: group_vars/HPE, check_model, bios-config, mac-discover, ilo-hostname,\n"
                    "        subscribe-redfish-events, + new security-hardening role (does not exist).\n"
                    "NO CHANGE: account-create, system-off/on, syslog-enable/disable, dhcp-disable,\n"
                    "        disable_dhcp_ntp.py, set_ilo_sntp_servers.py, configure_syslog.py.\n"
                    "VERIFY: configure_dns.py (Oem.Hpe.IPv6.DNSServers path needs iLO7 confirmation).\n\n"
                    "This is a PROPOSAL — nothing is applied until a human approves."
                )
            elif "workloadprofile" in p or "vran" in p or "group_vars" in p or "bios" in p:
                response = (
                    "CHANGE — group_vars/HPE (PROPOSED-28):\n\n"
                    "EL140 does NOT support individual BIOS attribute patching (BootMode, PciSlot1Enable,\n"
                    "MinProcIdlePower, LlcPrefetch, ProcessorConfigTDPLevel are absent in the 273-attr iLO7\n"
                    "registry). WorkloadProfile must be the exact string 'vRAN' to apply all 11 vRAN BIOS\n"
                    "settings atomically.\n\n"
                    "  # group_vars/HPE — ADD\n"
                    "  bios_attribute_value_workload_profile_vRAN: vRAN\n\n"
                    "Risk: none to existing e910t/e920t/e930t flows — new var only referenced in the EL140\n"
                    "bios-config block. The EL140 BIOS rejects any other WorkloadProfile value."
                )
            elif "registryprefix" in p or "subscribe" in p or "event" in p:
                response = (
                    "CHANGE — subscribe-redfish-events (PROPOSED-27):\n\n"
                    "`EventTypesForSubscription` is absent on all current HPE iLO; an EventTypes-based POST\n"
                    "fails. iLO7 requires `RegistryPrefixes`. Key finding: RegistryPrefixes is required on\n"
                    "BOTH iLO6 (e930t) AND iLO7 (EL140) — so this broadens the fix from EL140-only to ALL\n"
                    "current HPE iLO platforms. iLO5 marked unconfirmed."
                )
            elif "new role" in p or "does not exist" in p or "security" in p or "hardening" in p:
                response = (
                    "GAP — security-hardening role (PROPOSED-32): DOES NOT EXIST in the playbook.\n\n"
                    "The EL140 requires SNMP / HTTP / IPMI / SSDP disable and a login banner — there is no\n"
                    "security-hardening role today. This is a net-new role, not a modification. Also flagged:\n"
                    "PROPOSED-31 operational note — the NEBS 62°C inlet ambient caution threshold is not\n"
                    "Redfish-settable and needs a manual iLO UI step post-provisioning."
                )
            elif "ilo6" in p or "e930t" in p or "also affect" in p or "cross" in p:
                response = (
                    "Cross-platform findings — iLO7 deviations ALSO present on iLO6 (e930t):\n\n"
                    "  • NTP lives at /Managers/1/DateTime (not NetworkProtocol) on both iLO6 + iLO7\n"
                    "  • RegistryPrefixes required for event subscription on both\n"
                    "  • StaticNameServers(IPv6) bounded 1..3 on iLO7\n\n"
                    "Pulling real reference values from a live e930t (instead of placeholders) is what\n"
                    "exposed these — broadening required playbook scope beyond just the EL140."
                )
            elif "hostname" in p:
                response = (
                    "CHANGE — ilo-hostname (PROPOSED-25):\n\n"
                    "On iLO7, hostname PATCH must target `NetworkProtocol.HostName` — NOT the iLO5/iLO6 path\n"
                    "`EthernetInterfaces/1.Oem.Hpe.HostName`. Returns `ResetRequired` but the value is\n"
                    "immediately readable. ilo-reset timing confirmed ~133s — existing 3-min wait sufficient."
                )
            elif "risk" in p:
                response = (
                    "Risk per change (all LOW, version-controlled):\n\n"
                    "  group_vars/HPE       — new var only; zero impact on e910/920/930t flows\n"
                    "  check_model          — additive EL140 match condition\n"
                    "  bios-config          — EL140-gated block; existing platforms untouched\n"
                    "  mac-discover         — EL140 case via Chassis/1/NetworkAdapters\n"
                    "  ilo-hostname         — iLO7-gated path; iLO5/6 path retained\n"
                    "  subscribe-events     — RegistryPrefixes broadens to iLO6/7 (validated on both)\n"
                    "  security-hardening   — net-new role; no existing behavior changed\n\n"
                    "Every change maps to a PROPOSED test result as evidence. Nothing auto-applies."
                )
            elif "pr" in p or "open" in p or "apply" in p or "commit" in p:
                response = (
                    "Ready to open the PR with the 7 approved changes:\n\n"
                    "  branch: el140-ilo7-support → vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140\n"
                    "  15 role files touched · 7 CHANGE · 1 new role · evidence linked per change\n\n"
                    "This is a DIRECT ACTION — it requires HITL approval first (Gate 2 in the orchestration).\n"
                    "On approval I commit + open the PR for the automation team to review."
                )
            if response is None:
                response = (
                    "PlaybookAgent ready. I cross-reference live test results against the BMC Ansible playbook\n"
                    "and produce a formal change-spec for new platforms — a proposal, never an auto-apply.\n\n"
                    "Try: 'Generate the change-spec for the EL140 iLO7' · 'How many roles need changes?' ·\n"
                    "'What new role is required?' · 'Which deviations also affect iLO6?'"
                )

        # ══════════ CertificationAgent (UC-1) ══════════
        elif "certification" in agent_id or "cert" in agent_id:
            if "dmtf" in p or "conformance" in p or ("392" in p) or ("7 fail" in p) or ("triage" in p and "fail" in p):
                response = (
                    "DMTF Redfish Conformance — HPE Edgeline E930t · iLO 6 v1.57 (MEAKV-507)\n"
                    "Source: Redfish-Protocol-Validator v1.2.0 · real report from MTCE Lab.\n\n"
                    "  Summary — PASS: 392 · FAIL: 7 · WARN: 0 · NOT_TESTED: 31\n\n"
                    "The 7 failures, classified:\n"
                    "  • 6 × RESP_HEADERS_WWW_AUTHENTICATE — missing WWW-Authenticate header on\n"
                    "    401 responses (SessionService, Systems, AccountService, NetworkProtocol)\n"
                    "  • 1 × SEC_CERTS_CONFORM_X509V3 — cert decode fails on IPv6 hostname\n"
                    "    (Address family not supported)\n\n"
                    "VERDICT: All 7 are known-benign for VCPfe production operation. This exact\n"
                    "7-failure signature recurs IDENTICALLY on iLO5 3.06, iLO6 1.60, and ZT BMC\n"
                    "across the corpus — one triage rule certifies the whole fleet.\n"
                    "APEX auto-certifies with the cited production-irrelevance rule and attaches\n"
                    "evidence to JIRA — matching James Patchett's manual 'marked test passed'\n"
                    "decision 100%. → routed to HITL gate for engineer sign-off.\n"
                    "Manual effort saved: ~40 hr/firmware × 42 HPE reports in this corpus."
                )
                actions.append({"name": "classify_dmtf_failures", "result": "7 benign · auto-cert", "ts": int(time.time())})
            elif "samsung" in p or "pm9a3" in p or "thermal" in p or "fan" in p:
                response = (
                    "Samsung PM9A3 thermal regression (MEAKV-1792) — ZT Proteus.\n\n"
                    "Real finding from the corpus: on BMC .45, the SAMSUNG PM9A3\n"
                    "(MZQL21T9HCJR-00A07) temperature could not be read → fan controller defaults\n"
                    "to failsafe → all fans spike to 100% utilization. BMC .46 restores the\n"
                    "thermal read · lab-reproduced by downgrading .46 → .45.\n\n"
                    "CertificationAgent flags this as a deploy-blocking regression and hands to\n"
                    "SchemaWatch + UpgradeAdvisor: BLOCK BMC .45 wave to any PM9A3-equipped\n"
                    "subcloud · mandate BMC .46 minimum."
                )
            elif "samsung" not in p and ("samsung" in p):
                pass
            elif "ptu" in p or "performance" in p or "642" in p:
                response = (
                    "PTU Performance (MEAKV-642-646) — HPE E930t · iLO 6 v1.57 · Sapphire Rapids.\n\n"
                    "Intel PTU sustained CPU + memory stress: package power within TDP envelope,\n"
                    "no throttle events, memory bandwidth nominal. Outcome: PASS.\n"
                    "Perf baseline captured for cross-firmware regression tracking."
                )
            elif "sensor" in p or "1789" in p:
                response = (
                    "Functional Sensor (MEAKV-1789-1791) — ZT Proteus · BMC 3.02.\n\n"
                    "IPMI sensor list fully present + within thresholds (CPU DTS, PSU temps,\n"
                    "DIMM, fan, voltage rails). No UNR/UC/LC trips. Outcome: PASS.\n"
                    "No missing-sensor regression — direct contrast with the Samsung PM9A3\n"
                    "failure on BMC .45. Feeds the fleet thermal-telemetry baseline."
                )
            elif "bios" in p or "508" in p:
                response = (
                    "Functional BIOS (MEAKV-508-517) — ZT Triton · BMC 2.31.\n\n"
                    "BIOS attribute control via Redfish PATCH /Systems/Self/Bios/SD validated;\n"
                    "settings persist across host reboot. Note: PATCH during host boot returns\n"
                    "503 Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting → retry-after-boot\n"
                    "folded into the BMC playbook. Outcome: PASS."
                )
            elif "redfish" in p or "648" in p:
                response = (
                    "Functional Redfish (MEAKV-648-655) — ZT Proteus · BMC .46.\n\n"
                    "Systems / Managers / Chassis / TaskService walked; Manager.Reset task\n"
                    "lifecycle (New → Completed) verified; power + inventory responsive.\n"
                    "Outcome: PASS · no conformance triage needed here."
                )
            elif "soak" in p or "galene" in p or "longevity" in p:
                response = (
                    "Soak Test (E2E) — ZT Galene · BMC 1.13 · 7-day continuous (Apr 8–15 2025).\n\n"
                    "Monitored /var/log/user.log for PTP4L sync-error accumulation. PTP went\n"
                    "FAULTY → LISTENING on INIT_COMPLETE (expected init), then NO error\n"
                    "accumulation across the window. Outcome: PASS · longevity baseline logged."
                )
            elif "dell" in p or "r7615" in p or "idrac" in p or "vendor" in p:
                response = (
                    "Multi-vendor Sensor cert (MEAKV-1789) — Dell PowerEdge R7615 · iDRAC 7.10.50.10.\n\n"
                    "Newest fleet addition. iDRAC Redfish sensors normalized against HPE iLO and\n"
                    "ZT BMC; all thermal/voltage/fan within thresholds. The SAME MEAKV-1789 cert\n"
                    "catalog runs unchanged across HPE Edgeline, ZT, and Dell — the rule-set is\n"
                    "vendor-portable. Outcome: PASS."
                )
            elif "flexran" in p or "1860" in p or "ran" in p:
                response = (
                    "FlexRAN Settings (MEAKV-1860) — HPE E930t · iLO 6 v1.60.\n\n"
                    "Intel FlexRAN RT-optimized BIOS profile validated: C-state disabled,\n"
                    "P-state fixed, uncore pinned, HT per spec. RAN-ready. Cross-refs KB-2026-0118\n"
                    "RT tuning (kernel.sched_rt_runtime_us) for CU-UP latency under load. Outcome: PASS."
                )
            elif "platform" in p or "deploy" in p or "965" in p:
                response = (
                    "Platform Deployment (MEAKV-965) — HPE E930t · Wind River subcloud install.\n\n"
                    "Duplex controllers + worker enrolled to the system controller;\n"
                    "platform-integ alarms cleared post-deploy; distributed-cloud sync in-sync.\n"
                    "Outcome: PASS · subcloud added to fleet inventory for wave planning."
                )
            elif "hours" in p or "saved" in p or "40" in p or "roi" in p:
                response = (
                    "Manual baseline vs APEX — from the real corpus:\n\n"
                    "  • 118 firmware certification reports in this drop alone\n"
                    "  • ~40 hr per firmware validation manually (parse logs, triage Redfish\n"
                    "    conformance failures, cross-check sensors, write up, file JIRA)\n"
                    "  • APEX CertificationAgent: ~12–15 min per report end-to-end\n\n"
                    "At 118 reports: ~4,720 manual hours → ~28 hours with APEX.\n"
                    ">99% time reduction, and the triage verdicts match James's manual\n"
                    "decisions because APEX learned the production-irrelevance rules from\n"
                    "his own historical reports."
                )
            elif "hold" in p or "wave" in p or "recommend" in p or "deployment" in p:
                response = (
                    "Deployment recommendation across the current fleet:\n\n"
                    "  HOLD — ZT Proteus subclouds with Samsung PM9A3 drives on BMC .45\n"
                    "         (thermal regression MEAKV-1792 → 100% fan spike). Mandate .46.\n"
                    "  PROCEED — HPE E930t/E910t/E920t cert clean (DMTF 7-failure signature\n"
                    "            is known-benign), ZT Triton BMC 2.31, ZT Galene 1.13 (7-day soak),\n"
                    "            Dell R7615 sensor cert.\n\n"
                    "→ UpgradeAdvisor gates the PM9A3 sites; everything else is wave-eligible."
                )
            if response is None:
                response = (
                    "CertificationAgent (Verizon Far Edge) ready. Loaded the real MTCE Lab corpus:\n"
                    "118 firmware reports · HPE Edgeline (E910t/E920t/E930t) · ZT (Proteus/Triton/\n"
                    "Galene) · Dell R7615 · WRCP 21.05p6→21.12p10.\n\n"
                    "Try: 'Triage the DMTF conformance failures on E930t iLO6 1.57' ·\n"
                    "'Show the Samsung PM9A3 thermal finding' · 'PTU performance on E930t' ·\n"
                    "'How many hours does APEX save across 118 reports?' ·\n"
                    "'What's the wave deployment recommendation?'"
                )

        # ══════════ SchemaWatchAgent (UC-2) ══════════
        elif "schema" in agent_id:
            if "samsung" in p or "pm9a3" in p or "thermal" in p or "fan" in p or "regression" in p or "1792" in p:
                response = (
                    "REGRESSION DETECTED — Samsung PM9A3 thermal read (MEAKV-1792).\n\n"
                    "BMC firmware .45 fails to read the SAMSUNG PM9A3 (MZQL21T9HCJR-00A07)\n"
                    "drive temperature → fan controller failsafe → 100% fan utilization\n"
                    "(acoustic + power impact across the subcloud). BMC .46 restores the read.\n"
                    "Lab-reproduced: downgrade .46 → .45 reproduces the spike.\n\n"
                    "Blast radius: every subcloud running BMC .45 with PM9A3 drives.\n"
                    "→ UpgradeAdvisor: BLOCK .45 wave to PM9A3 sites · mandate .46 minimum.\n"
                    "This is the proactive catch — found in lab before it hit a production wave."
                )
            elif "503" in p or "troubleshoot" in p or "transient" in p or "redfishdbreset" in p or "boot" in p:
                response = (
                    "Transient classified — Redfish 503 during host boot (ZT Proteus BMC .43).\n\n"
                    "Symptom: PATCH /Systems/Self/Bios/SD → 503\n"
                    "  Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting\n"
                    "Root cause: host reboot / Redfish inventory processing window.\n"
                    "Remediation: POST AMIManager.RedfishDBReset {ResetAll} clears the stuck DB,\n"
                    "then PATCH succeeds. Captured + folded into the MentorAgent BMC-playbook KB."
                )
            elif "drift" in p or "breaking" in p or "v1.14" in p or "v1.16" in p:
                response = (
                    "Schema drift watch — Redfish baseline vs current across the fleet.\n\n"
                    "The real corpus shows controller-firmware deltas (iLO5 3.06 → iLO6 1.57 →\n"
                    "1.60 → 1.68 on HPE; BMC .43 → .45 → .46 → 2.31 → 3.02 on ZT). SchemaWatch\n"
                    "diffs the Redfish surface between firmware revs and flags any field/path that\n"
                    "moved or any sensor that disappeared (e.g. the PM9A3 thermal read on .45).\n"
                    "Detection happens BEFORE the cert cycle, leaving runway to remediate."
                )
            elif "block" in p or "wave" in p or "proceed" in p:
                response = (
                    "SchemaWatch wave gate:\n"
                    "  BLOCK — BMC .45 to PM9A3 subclouds (thermal regression confirmed)\n"
                    "  WATCH — early-rev BMC .43 (Redfish 503-during-boot transient; needs retry)\n"
                    "  CLEAR — BMC .46, 2.31, 3.02; HPE iLO6 1.57/1.60; Dell iDRAC 7.10.50.10\n"
                    "→ hands the block list to UpgradeAdvisor for wave planning."
                )
            if response is None:
                response = (
                    "SchemaWatchAgent (Verizon Far Edge) ready. Watching firmware-rev deltas\n"
                    "across the real fleet for regressions + Redfish drift.\n\n"
                    "Try: 'Show the Samsung PM9A3 regression' · 'Explain the Redfish 503 transient\n"
                    "on BMC .43' · 'What firmware should we block from the next wave?'"
                )

        # ══════════ UpgradeAdvisorAgent (UC-3) ══════════
        elif "upgrade" in agent_id:
            if "21.05" in p or "21.12" in p or "path" in p or "2105" in p or "2112" in p:
                response = (
                    "Upgrade path validation — ZT Proteus · WRCP 21.05p6 → 21.12p10.\n\n"
                    "Real subcloud upgrade from the corpus (welktxef-d931856-008, anonymized):\n"
                    "  Baseline: software_version 21.05 · pre-upgrade out-of-sync alarms\n"
                    "            (kubernetes + load) — expected during staging\n"
                    "  Upgrade:  21.05-30 → 21.12-46 completed · rook-ceph-apps reconciled\n"
                    "  Post:     fm alarm-list clean · application-list reconciled · BMC .46\n\n"
                    "VERDICT: path certified end-to-end. Added to the upgrade compatibility\n"
                    "matrix → feeds the wave-deployment risk model."
                )
            elif "samsung" in p or "pm9a3" in p or "block" in p:
                response = (
                    "Wave gate — PM9A3 thermal regression in play.\n\n"
                    "UpgradeAdvisor BLOCKS BMC .45 deployment to any subcloud with Samsung PM9A3\n"
                    "drives (MEAKV-1792: temp unreadable → 100% fans). Minimum safe BMC = .46.\n"
                    "All other ZT Proteus/Triton/Galene firmware paths are wave-eligible."
                )
            elif "risk" in p or "historical" in p or "hitl" in p or "fail" in p:
                response = (
                    "Historical-risk scoring (UC-3):\n\n"
                    "UpgradeAdvisor scores each upgrade path on (a) prior failure history for the\n"
                    "platform+firmware combo, (b) whether the target firmware carries a known\n"
                    "regression (e.g. BMC .45 PM9A3), and (c) blast radius. High-risk paths route\n"
                    "to a HITL approval gate. The .45 PM9A3 case is the canonical high-risk block;\n"
                    "the 21.05p6 → 21.12p10 Proteus path is low-risk (validated, alarms clear)."
                )
            elif "platform" in p or "deploy" in p or "965" in p or "subcloud" in p:
                response = (
                    "Platform deployment readiness (MEAKV-965) — HPE E930t subcloud.\n\n"
                    "Duplex controllers + worker enrolled to the system controller; platform-integ\n"
                    "alarms cleared; distributed-cloud sync in-sync. Subcloud added to fleet\n"
                    "inventory. Ready for workload + future wave upgrades."
                )
            if response is None:
                response = (
                    "UpgradeAdvisorAgent (Verizon Far Edge) ready. Validates firmware + WRCP\n"
                    "upgrade paths against the real corpus and scores deployment risk.\n\n"
                    "Try: 'Validate WRCP 21.05p6 → 21.12p10 on Proteus' · 'Why block BMC .45 from\n"
                    "the wave?' · 'Score the risk of the Proteus upgrade path.'"
                )

        # ══════════ MentorAgent (UC-4) ══════════
        else:
            if "samsung" in p or "pm9a3" in p or "thermal" in p or "1792" in p:
                response = (
                    "KB · Samsung PM9A3 thermal on ZT BMC (MEAKV-1792)\n\n"
                    "Known issue: BMC firmware .45 cannot read SAMSUNG PM9A3 (MZQL21T9HCJR-00A07)\n"
                    "drive temperature; fans default to 100%. Fix: upgrade BMC to .46+.\n"
                    "Verbatim from James Patchett's validation report — no paraphrase, full lineage\n"
                    "to the source doc in synthetic-data/verizon_far_edge/real_test_reports/."
                )
            elif "503" in p or "redfishdbreset" in p or "boot" in p:
                response = (
                    "KB · Redfish 503 ServiceTemporarilyUnavailable during host boot (ZT BMC)\n\n"
                    "Cause: host reboot / Redfish inventory processing window.\n"
                    "Workaround: POST /Managers/Self/Actions/Oem/AMIManager.RedfishDBReset\n"
                    "  {\"RedfishDBResetType\": \"ResetAll\"} then retry the request.\n"
                    "Cited verbatim from the .43 BMC troubleshooting report."
                )
            elif "dmtf" in p or "conformance" in p or "www-authenticate" in p or "x509" in p or "x.509" in p:
                response = (
                    "KB · DMTF Redfish Conformance — known-benign failures for VCPfe\n\n"
                    "The Redfish Protocol Validator reports 5–7 FAILs on HPE iLO and ZT BMC that\n"
                    "are NOT relevant to VCPfe production operation:\n"
                    "  • WWW-Authenticate header missing on 401 responses\n"
                    "  • X.509 cert decode fails on IPv6 hostname (address family unsupported)\n"
                    "Standard practice (per James Patchett): upload to JIRA, mark test passed.\n"
                    "APEX automates exactly this verdict."
                )
            elif "flexran" in p or "rt" in p or "latency" in p or "kb-2026-0118" in p or "tuning" in p:
                response = (
                    "KB-2026-0118 · CU-UP latency under default RT tuning\n\n"
                    "Symptom: CU-UP P99 latency 6–8 ms vs 5 ms threshold under sustained load.\n"
                    "Root cause: kernel.sched_rt_runtime_us default (950000) too low.\n"
                    "Workaround: set sched_rt_runtime_us=980000 (99-rt-tune.conf), reboot in MW.\n"
                    "Ties to FlexRAN BIOS profile validation (MEAKV-1860) on E930t iLO6 1.60."
                )
            elif "upgrade" in p or "rollback" in p or "path" in p:
                response = (
                    "KB · Firmware/WRCP upgrade + rollback (far edge)\n\n"
                    "Validated path in the corpus: WRCP 21.05p6 → 21.12p10 on ZT Proteus\n"
                    "(out-of-sync alarms expected during staging, clear post-upgrade).\n"
                    "Rollback: BMC firmware is downgrade-capable (.46 → .45 reproduced the PM9A3\n"
                    "issue in lab), so always validate the target rev for known regressions first."
                )
            if response is None:
                response = (
                    "MentorAgent (Verizon Far Edge) ready. KB Q&A with verbatim citations from\n"
                    "James Patchett's real validation reports — no hallucination, full lineage.\n\n"
                    "Try: 'Known issue with Samsung PM9A3 on ZT BMC?' · 'How do I fix the Redfish\n"
                    "503 during boot?' · 'Are the DMTF conformance failures a real problem?' ·\n"
                    "'How do I work around KB-2026-0118?'"
                )

        actions.append({"name": "answer_drafted", "agent_id": agent_id, "ts": int(time.time())})
        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions,
        }

    def get_available_agents(self) -> list:
        """Return list of available agents."""
        return [
            {"id": "cre-underwrite-bot", "name": "CREUnderwriteBot", "description": "Commercial Real Estate Underwriting Assistant - Risk analysis, premium calculation, deal recommendations", "category": "insurance_underwriting"},
            {"id": "underwrite-bot", "name": "UnderwriteBot", "description": "Insurance underwriting assistant", "category": "insurance_underwriting"},
            {"id": "shopper-bot", "name": "ShopperBot", "description": "AI shopping assistant - search, compare, buy", "category": "retail"},
            {"id": "invoice-bot", "name": "InvoiceBot", "description": "Invoice processing and validation", "category": "financial"},
            {"id": "claims-bot", "name": "ClaimsBot", "description": "Claims adjudication", "category": "healthcare"},
            {"id": "talent-bot", "name": "TalentBot", "description": "Resume screening", "category": "hr"},
            {"id": "po-bot", "name": "POBot", "description": "Purchase order processing", "category": "manufacturing"},
            {"id": "intake-bot", "name": "IntakeBot", "description": "Patient intake processing", "category": "healthcare"},
            # Aerospace & Defense agents (Essex Industries)
            {"id": "contract-bot", "name": "ContractBot", "description": "Defense contract analysis, pricing prediction, RFP support - GPT-5.4", "category": "aerospace_defense"},
            {"id": "cnc-bot", "name": "CNCBot", "description": "CNC programming assistance, G-code review, machining optimization - GPT-5.4", "category": "aerospace_defense"},
            {"id": "workorder-bot", "name": "WorkOrderBot", "description": "Work order management, ERP read/write, NCR creation - GPT-5.4", "category": "aerospace_defense"},
            # STP Phase 2 — Nuclear Operations & Reliability agents
            {"id": "chatstp",            "name": "ChatSTP",          "description": "STP Nuclear · Enterprise knowledge router · classifies queries and delegates to PolicyAgent / MaintenanceAgent / DiagnosticsAgent / ReliabilityAgent", "category": "nuclear_operations"},
            {"id": "policy-agent",       "name": "PolicyAgent",       "description": "STP Nuclear · UC-1 · Cite-verbatim policy & procedure lookup over the STP-4xx, 0POP-, 0PMP-, and Tech Spec corpus", "category": "nuclear_operations"},
            {"id": "maintenance-agent",  "name": "MaintenanceAgent",  "description": "STP Nuclear · UC-2 · Equipment PM history with engineer attribution from Oracle PMHISTORY", "category": "nuclear_operations"},
            {"id": "diagnostics-agent",  "name": "DiagnosticsAgent",  "description": "STP Nuclear · UC-3 · Failure-mode aggregation across the work-package corpus with cited WO evidence", "category": "nuclear_operations"},
            {"id": "reliability-agent",  "name": "ReliabilityAgent",  "description": "STP Nuclear · UC-4 · Predictive maintenance — RUL forecast + anomaly detection + risk score + PM advance recommendation via ApexSignal", "category": "nuclear_operations"},
            # Agentic Enterprise (66 Degrees vendor-neutral demos)
            {"id": "orchestrator-agent", "name": "OrchestratorAgent", "description": "Agentic Enterprise · UC-1 · Supply Chain Orchestrator — multi-tool agent that detects shortages, ranks alternative suppliers, drafts POs, and routes to human approval with full reasoning trace.", "category": "agentic_enterprise"},
            {"id": "concierge-agent",    "name": "ConciergeAgent",    "description": "Agentic Enterprise · UC-2 · Cruise Concierge — stateful conversational agent with RAG over guest-services FAQ, booking modification, sentiment monitoring, and seamless handoff to a human agent.", "category": "agentic_enterprise"},
            {"id": "lease-agent",        "name": "LeaseAgent",        "description": "Agentic Enterprise · UC-3 · Lease Extraction — extracts tenant, expiration, and liability clauses from commercial lease documents, ingests to DuckDB, and answers SQL queries against the structured table.", "category": "agentic_enterprise"},
        ]


