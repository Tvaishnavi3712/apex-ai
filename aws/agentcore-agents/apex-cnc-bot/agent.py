"""
Apex CNC Bot - AgentCore Agent for CNC programming assistance
Uses Claude Opus 4.6 for G-code analysis and optimization.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from typing import List, Optional
import re

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are CNCBot, an AI assistant specialized in CNC programming assistance for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Review and analyze G-code programs for syntax and safety issues
2. Validate feeds and speeds against material specifications
3. Suggest optimizations based on best practices
4. Reference similar historical programs
5. Provide machining guidance for aerospace alloys

Material expertise:
- Ti-6Al-4V (Titanium): SFM 100-150, work hardening, high-pressure coolant required
- 7075-T6 (Aluminum): SFM 800-1500, aggressive cuts OK, watch chip welding
- 15-5 PH (Stainless): SFM 150-250, use sharp tools
- Inconel 718: SFM 60-100, very difficult, minimize heat

Machine types supported: Mazak, DMG Mori, Haas, Hermle

Safety priorities:
- Always check Z clearance on rapids (minimum 0.25")
- Verify spindle speed limits
- Confirm coolant activation before cutting
- Flag potential collision risks

You ASSIST the machinist - all recommendations require human approval.
Be precise and cite specific line numbers when identifying issues."""

# Material specifications
MATERIALS = {
    "Ti-6Al-4V": {
        "sfm_range": (100, 150),
        "feed_per_tooth": (0.002, 0.006),
        "coolant": "high_pressure",
        "notes": "Work hardening material - maintain chip load"
    },
    "7075-T6": {
        "sfm_range": (800, 1500),
        "feed_per_tooth": (0.004, 0.012),
        "coolant": "flood",
        "notes": "Aggressive cuts OK, watch for chip welding"
    },
    "15-5PH": {
        "sfm_range": (150, 250),
        "feed_per_tooth": (0.003, 0.008),
        "coolant": "flood",
        "notes": "Stainless - use sharp tools"
    },
    "Inconel-718": {
        "sfm_range": (60, 100),
        "feed_per_tooth": (0.002, 0.005),
        "coolant": "high_pressure_required",
        "notes": "Very difficult material - minimize heat"
    }
}


@tool
def parse_gcode(gcode: str) -> dict:
    """
    Parse G-code program into structured blocks for analysis.

    Args:
        gcode: G-code program text

    Returns:
        Parsed blocks with codes, values, and line numbers
    """
    blocks = []
    lines = gcode.strip().split('\n')

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('(') or line.startswith(';'):
            continue

        block = {
            "line_number": i + 1,
            "raw": line,
            "codes": [],
            "values": {}
        }

        # Extract G codes
        g_codes = re.findall(r'G(\d+\.?\d*)', line, re.IGNORECASE)
        block["codes"].extend([f"G{c}" for c in g_codes])

        # Extract M codes
        m_codes = re.findall(r'M(\d+)', line, re.IGNORECASE)
        block["codes"].extend([f"M{c}" for c in m_codes])

        # Extract axis values
        for axis in ['X', 'Y', 'Z', 'A', 'B', 'C']:
            match = re.search(rf'{axis}(-?\d+\.?\d*)', line, re.IGNORECASE)
            if match:
                block["values"][axis] = float(match.group(1))

        # Extract feed rate
        f_match = re.search(r'F(\d+\.?\d*)', line, re.IGNORECASE)
        if f_match:
            block["values"]["F"] = float(f_match.group(1))

        # Extract spindle speed
        s_match = re.search(r'S(\d+)', line, re.IGNORECASE)
        if s_match:
            block["values"]["S"] = int(s_match.group(1))

        blocks.append(block)

    return {
        "blocks": blocks,
        "total_lines": len(lines),
        "parsed_blocks": len(blocks)
    }


@tool
def analyze_feeds_speeds(
    spindle_rpm: int,
    feed_rate: float,
    tool_diameter: float,
    material: str
) -> dict:
    """
    Analyze feeds and speeds against material recommendations.

    Args:
        spindle_rpm: Spindle speed in RPM
        feed_rate: Feed rate in IPM
        tool_diameter: Tool diameter in inches
        material: Material being machined

    Returns:
        Analysis with recommendations
    """
    material_params = MATERIALS.get(material, MATERIALS["7075-T6"])

    # Calculate SFM
    sfm = (spindle_rpm * tool_diameter * 3.14159) / 12
    sfm_min, sfm_max = material_params["sfm_range"]

    issues = []
    recommendations = []

    if sfm > sfm_max:
        recommended_rpm = int((sfm_max * 12) / (tool_diameter * 3.14159))
        issues.append({
            "type": "warning",
            "category": "spindle_speed",
            "message": f"SFM {sfm:.0f} exceeds recommended max {sfm_max} for {material}",
            "recommendation": f"Reduce spindle to S{recommended_rpm}"
        })
    elif sfm < sfm_min:
        recommended_rpm = int((sfm_min * 12) / (tool_diameter * 3.14159))
        issues.append({
            "type": "info",
            "category": "spindle_speed",
            "message": f"SFM {sfm:.0f} below recommended min {sfm_min} for {material}",
            "recommendation": f"Consider increasing spindle to S{recommended_rpm}"
        })

    return {
        "calculated_sfm": round(sfm, 0),
        "recommended_sfm_range": material_params["sfm_range"],
        "coolant_requirement": material_params["coolant"],
        "material_notes": material_params["notes"],
        "issues": issues,
        "assessment": "OK" if not issues else "REVIEW_REQUIRED"
    }


@tool
def check_safety(gcode: str) -> dict:
    """
    Check G-code for safety issues.

    Args:
        gcode: G-code program text

    Returns:
        Safety analysis with warnings and critical issues
    """
    issues = []
    lines = gcode.strip().split('\n')
    current_z = None
    has_coolant = False
    spindle_started = False
    min_z_clearance = 0.25

    for i, line in enumerate(lines):
        line_num = i + 1
        line = line.strip().upper()

        # Check for coolant
        if 'M8' in line or 'M08' in line:
            has_coolant = True

        # Check for spindle start
        if 'M3' in line or 'M03' in line:
            spindle_started = True
            if not has_coolant:
                issues.append({
                    "line": line_num,
                    "type": "warning",
                    "category": "coolant",
                    "message": "Spindle started without coolant command",
                    "recommendation": "Add M8 (coolant on) before spindle start"
                })

        # Check Z clearance on rapids
        if 'G0' in line or 'G00' in line:
            z_match = re.search(r'Z(-?\d+\.?\d*)', line)
            if z_match:
                z_val = float(z_match.group(1))
                if z_val < min_z_clearance and current_z is not None and current_z > z_val:
                    issues.append({
                        "line": line_num,
                        "type": "critical",
                        "category": "rapid_clearance",
                        "message": f"Rapid to Z{z_val} - insufficient clearance",
                        "recommendation": f"Increase Z clearance to at least {min_z_clearance}"
                    })
                current_z = z_val

        # Track Z position
        z_match = re.search(r'Z(-?\d+\.?\d*)', line)
        if z_match:
            current_z = float(z_match.group(1))

    critical = [i for i in issues if i["type"] == "critical"]
    warnings = [i for i in issues if i["type"] == "warning"]

    return {
        "critical_issues": critical,
        "warnings": warnings,
        "total_issues": len(issues),
        "assessment": "STOP" if critical else ("REVIEW" if warnings else "OK"),
        "coolant_detected": has_coolant
    }


@tool
def suggest_optimizations(gcode: str, material: str) -> dict:
    """
    Suggest optimizations for a G-code program.

    Args:
        gcode: G-code program text
        material: Material being machined

    Returns:
        Optimization suggestions
    """
    optimizations = []
    lines = gcode.strip().split('\n')

    # Count move types
    rapid_count = sum(1 for line in lines if 'G0' in line.upper() or 'G00' in line.upper())
    cutting_count = sum(1 for line in lines if 'G1' in line.upper() or 'G01' in line.upper())

    if rapid_count > cutting_count * 0.5:
        optimizations.append({
            "type": "cycle_time",
            "message": "High ratio of rapid moves to cutting moves",
            "recommendation": "Consider toolpath optimization to reduce air cutting",
            "potential_savings": "5-15% cycle time reduction"
        })

    # Check for constant surface speed
    has_css = any('G96' in line.upper() for line in lines)
    if not has_css and material in ["Ti-6Al-4V", "Inconel-718"]:
        optimizations.append({
            "type": "surface_finish",
            "message": f"Constant surface speed (G96) not used for {material}",
            "recommendation": "Consider G96 for improved surface finish",
            "potential_savings": "Improved surface finish, reduced tool wear"
        })

    # Material-specific recommendations
    material_params = MATERIALS.get(material, {})
    if material_params.get("coolant") == "high_pressure_required":
        optimizations.append({
            "type": "tool_life",
            "message": f"{material} requires high-pressure coolant",
            "recommendation": "Ensure high-pressure coolant (1000+ PSI) is enabled",
            "potential_savings": "50-100% improvement in tool life"
        })

    return {
        "optimizations": optimizations,
        "optimization_count": len(optimizations),
        "rapid_move_count": rapid_count,
        "cutting_move_count": cutting_count,
        "material": material
    }


@tool
def find_similar_programs(part_number: str, material: str) -> dict:
    """
    Find similar historical programs for reference.

    Args:
        part_number: Part number being programmed
        material: Material type

    Returns:
        Similar programs with lessons learned
    """
    # Real implementation would query program repository
    return {
        "similar_programs": [
            {
                "program_name": f"{part_number[:-3]}001_Mazak.nc",
                "similarity": 0.85,
                "cycle_time": "45 min",
                "machine": "Mazak Integrex",
                "notes": "Previous revision, similar geometry",
                "lessons_learned": [
                    "Used trochoidal milling for deep pockets",
                    "Required fixture support for thin wall section"
                ]
            },
            {
                "program_name": "TG-5841_Mazak_Roughing.nc",
                "similarity": 0.72,
                "cycle_time": "38 min",
                "machine": "Mazak Variaxis",
                "notes": "Similar throttle grip, trochoidal milling",
                "lessons_learned": [
                    "Reduced chip load on finish passes",
                    "Added air blast for chip evacuation"
                ]
            }
        ],
        "total_found": 2,
        "source": "CNC Program Repository"
    }


# Create the Strands agent with Claude Opus 4.6
model = BedrockModel(
    model_id="us.anthropic.claude-opus-4-6-v1",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        parse_gcode,
        analyze_feeds_speeds,
        check_safety,
        suggest_optimizations,
        find_similar_programs
    ]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
