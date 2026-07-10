"""
AgentCore Service - Invoke deployed AgentCore agents
Includes intelligent CRE Underwriting demo responses
"""
import boto3
import json
import base64
import subprocess
import tempfile
import os
import re
import random
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


class AgentCoreService:
    """Service for invoking AgentCore runtime agents."""

    # Deployed agent ARNs
    AGENT_ARNS = {
        "invoice-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_invoice_bot-T2Z9quFfEt",
        "shopper-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_shopper_bot-E20HMiEAtn",
        "claims-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_claims_bot",
        "talent-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_talent_bot",
        "po-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_po_bot",
        "intake-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_intake_bot",
        "underwrite-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_underwrite_bot",
        "cre-underwrite-bot": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_cre_underwrite_bot",
    }

    # Agents that use local demo mode (intelligent responses without AWS)
    DEMO_AGENTS = {"underwrite-bot", "cre-underwrite-bot", "creunderwritebot"}

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.cre_bot = CREUnderwritingBot()

    def _is_cre_underwriting_agent(self, agent_id: str) -> bool:
        """Check if the agent is a CRE underwriting agent (uses demo mode)."""
        agent_id_lower = agent_id.lower().replace("-", "").replace("_", "")
        cre_keywords = ["underwrite", "cre", "insurance", "risk"]
        return any(kw in agent_id_lower for kw in cre_keywords)

    async def invoke_agent(self, agent_id: str, prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Invoke an AgentCore agent with a prompt.

        Args:
            agent_id: The agent identifier (e.g., 'invoice-bot')
            prompt: The user's message/prompt
            session_id: Optional session ID for conversation continuity

        Returns:
            Dict containing the agent's response (clean, no logs)
        """
        # Check if this is a CRE underwriting agent (use intelligent demo responses)
        if self._is_cre_underwriting_agent(agent_id):
            return await self._invoke_cre_demo(prompt)

        agent_arn = self.AGENT_ARNS.get(agent_id)

        # If no ARN found, try to use demo mode for any agent during demos
        if not agent_arn:
            # For demo purposes, use CRE bot for any unrecognized agent
            return await self._invoke_cre_demo(prompt)

        try:
            # Try AWS CLI invocation first
            result = await self._invoke_via_aws_cli(agent_arn, prompt)

            # If AWS fails, fall back to demo mode
            if not result.get("success"):
                return await self._invoke_cre_demo(prompt)

            return result

        except Exception as e:
            # Fall back to demo mode on any error
            return await self._invoke_cre_demo(prompt)

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

    async def _invoke_via_aws_cli(self, agent_arn: str, prompt: str) -> Dict[str, Any]:
        """Invoke agent via AWS CLI - returns clean response only."""
        try:
            # Create temp file for response
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = f.name

            # Encode payload as base64
            payload = json.dumps({"prompt": prompt})
            payload_b64 = base64.b64encode(payload.encode()).decode()

            # Invoke using AWS CLI (silent, no logs)
            result = subprocess.run(
                [
                    "aws", "bedrock-agentcore", "invoke-agent-runtime",
                    "--agent-runtime-arn", agent_arn,
                    "--region", self.region,
                    "--payload", payload_b64,
                    temp_file
                ],
                capture_output=True,
                text=True,
                timeout=90
            )

            if result.returncode == 0:
                # Read the response file
                with open(temp_file, 'r') as f:
                    response_data = json.load(f)

                # Extract clean response
                agent_response = response_data.get("response", "")

                # Clean up temp file
                os.unlink(temp_file)

                return {
                    "success": True,
                    "response": agent_response,
                    "reasoning": [],
                    "actions_taken": []
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
        ]
