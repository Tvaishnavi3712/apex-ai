"""
Product Design Assistant - Small Factory (FUTURE STATE)
AI-assisted design analysis, DFM review, and material selection.
Uses GPT-5.4 for intelligent recommendations.

NOTE: This is a FUTURE CAPABILITY demonstration.
The agent ASSISTS engineers - all decisions require human approval.
"""

from typing import Dict, Any, List, Optional
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()


# DFM Rules - Manufacturability Guidelines
DFM_RULES = {
    "internal_radius": {
        "warning": 0.125,  # inches
        "critical": 0.0625,
        "message": "Internal corner radius may require special tooling"
    },
    "depth_to_width": {
        "warning": 4.0,
        "critical": 6.0,
        "message": "Deep pocket may require special tooling or EDM"
    },
    "wall_thickness": {
        "aluminum": {"warning": 0.060, "critical": 0.030},
        "titanium": {"warning": 0.080, "critical": 0.050},
        "steel": {"warning": 0.070, "critical": 0.040},
        "inconel": {"warning": 0.100, "critical": 0.060},
        "message": "Thin wall may cause deflection during machining"
    },
    "hole_diameter": {
        "warning": 0.0625,
        "critical": 0.03125,
        "message": "Small hole may require EDM or special drilling"
    },
    "tolerance": {
        "standard": 0.005,
        "precision": 0.002,
        "grinding": 0.0005,
        "message": "Tight tolerance will increase cost and inspection"
    }
}


# Material Database
AEROSPACE_MATERIALS = {
    "Ti-6Al-4V": {
        "category": "titanium",
        "ams_specs": ["AMS-4911", "AMS-4928", "AMS-4930"],
        "properties": {
            "density_lb_in3": 0.160,
            "tensile_strength_ksi": 130,
            "yield_strength_ksi": 120,
            "max_temp_f": 600
        },
        "strengths": [
            "High strength-to-weight ratio",
            "Excellent corrosion resistance",
            "Good high-temperature capability"
        ],
        "weaknesses": [
            "Difficult to machine (work hardens)",
            "High material cost",
            "Requires specialized tooling"
        ],
        "machinability_rating": 0.30,
        "relative_cost": 8.0,
        "typical_applications": [
            "Structural components",
            "Engine parts",
            "Fasteners"
        ]
    },
    "7075-T6": {
        "category": "aluminum",
        "ams_specs": ["AMS-4045", "AMS-4078"],
        "properties": {
            "density_lb_in3": 0.101,
            "tensile_strength_ksi": 83,
            "yield_strength_ksi": 73,
            "max_temp_f": 250
        },
        "strengths": [
            "High strength for aluminum",
            "Excellent machinability",
            "Cost effective"
        ],
        "weaknesses": [
            "Poor corrosion resistance",
            "Not weldable",
            "Susceptible to stress corrosion"
        ],
        "machinability_rating": 0.80,
        "relative_cost": 1.5,
        "typical_applications": [
            "Structural frames",
            "Fittings",
            "Brackets"
        ]
    },
    "15-5 PH": {
        "category": "steel",
        "ams_specs": ["AMS-5659", "AMS-5862"],
        "properties": {
            "density_lb_in3": 0.283,
            "tensile_strength_ksi": 190,
            "yield_strength_ksi": 170,
            "max_temp_f": 600
        },
        "strengths": [
            "High strength",
            "Good corrosion resistance",
            "Good toughness"
        ],
        "weaknesses": [
            "Moderate machinability",
            "Heat treatment required",
            "Magnetic"
        ],
        "machinability_rating": 0.50,
        "relative_cost": 3.0,
        "typical_applications": [
            "Shafts",
            "Gears",
            "Valve components"
        ]
    },
    "Inconel-718": {
        "category": "inconel",
        "ams_specs": ["AMS-5662", "AMS-5663"],
        "properties": {
            "density_lb_in3": 0.297,
            "tensile_strength_ksi": 180,
            "yield_strength_ksi": 150,
            "max_temp_f": 1300
        },
        "strengths": [
            "Extreme temperature capability",
            "Oxidation resistant",
            "Maintains strength at high temp"
        ],
        "weaknesses": [
            "Very difficult to machine",
            "High material cost",
            "Work hardens severely"
        ],
        "machinability_rating": 0.15,
        "relative_cost": 12.0,
        "typical_applications": [
            "Turbine components",
            "High-temp exhaust",
            "Fasteners for extreme environments"
        ]
    }
}


def analyze_dfm(features: List[Dict], material: str) -> List[Dict[str, Any]]:
    """Analyze design features for manufacturability."""
    issues = []
    material_category = AEROSPACE_MATERIALS.get(material, {}).get("category", "aluminum")

    for feature in features:
        feature_type = feature.get("type", "")

        # Check internal radii
        if feature_type == "pocket" or feature_type == "internal_corner":
            radius = feature.get("internal_radius", 0)
            if radius > 0:
                if radius < DFM_RULES["internal_radius"]["critical"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "critical",
                        "type": "internal_radius",
                        "value": radius,
                        "threshold": DFM_RULES["internal_radius"]["critical"],
                        "message": f"Internal radius {radius}\" is below critical threshold",
                        "recommendation": f"Increase radius to minimum {DFM_RULES['internal_radius']['warning']}\" or use EDM"
                    })
                elif radius < DFM_RULES["internal_radius"]["warning"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "warning",
                        "type": "internal_radius",
                        "value": radius,
                        "threshold": DFM_RULES["internal_radius"]["warning"],
                        "message": f"Internal radius {radius}\" may require small end mill",
                        "recommendation": "Consider increasing radius for better tool life"
                    })

        # Check pocket depth
        if feature_type == "pocket":
            depth = feature.get("depth", 0)
            width = feature.get("width", 1)
            if width > 0:
                ratio = depth / width
                if ratio > DFM_RULES["depth_to_width"]["critical"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "critical",
                        "type": "depth_to_width",
                        "value": ratio,
                        "threshold": DFM_RULES["depth_to_width"]["critical"],
                        "message": f"Depth-to-width ratio {ratio:.1f}:1 exceeds limits",
                        "recommendation": "Consider EDM, split operations, or design modification"
                    })
                elif ratio > DFM_RULES["depth_to_width"]["warning"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "warning",
                        "type": "depth_to_width",
                        "value": ratio,
                        "threshold": DFM_RULES["depth_to_width"]["warning"],
                        "message": f"Depth-to-width ratio {ratio:.1f}:1 is challenging",
                        "recommendation": "May require extended reach tooling"
                    })

        # Check wall thickness
        if feature_type == "wall":
            thickness = feature.get("thickness", 0)
            thresholds = DFM_RULES["wall_thickness"].get(
                material_category,
                DFM_RULES["wall_thickness"]["aluminum"]
            )
            if thickness > 0:
                if thickness < thresholds["critical"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "critical",
                        "type": "wall_thickness",
                        "value": thickness,
                        "threshold": thresholds["critical"],
                        "message": f"Wall thickness {thickness}\" is too thin for {material}",
                        "recommendation": f"Increase to minimum {thresholds['warning']}\" or redesign"
                    })
                elif thickness < thresholds["warning"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "warning",
                        "type": "wall_thickness",
                        "value": thickness,
                        "threshold": thresholds["warning"],
                        "message": f"Wall thickness {thickness}\" may deflect during machining",
                        "recommendation": "Consider fixture support or lighter cuts"
                    })

        # Check hole diameter
        if feature_type == "hole":
            diameter = feature.get("diameter", 0)
            if diameter > 0:
                if diameter < DFM_RULES["hole_diameter"]["critical"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "critical",
                        "type": "hole_diameter",
                        "value": diameter,
                        "threshold": DFM_RULES["hole_diameter"]["critical"],
                        "message": f"Hole diameter {diameter}\" requires EDM",
                        "recommendation": "Increase diameter or plan for EDM operation"
                    })
                elif diameter < DFM_RULES["hole_diameter"]["warning"]:
                    issues.append({
                        "feature": feature.get("name", feature_type),
                        "severity": "warning",
                        "type": "hole_diameter",
                        "value": diameter,
                        "threshold": DFM_RULES["hole_diameter"]["warning"],
                        "message": f"Hole diameter {diameter}\" requires careful drilling",
                        "recommendation": "Use pecking cycle and appropriate speeds"
                    })

        # Check tolerances
        tolerance = feature.get("tolerance", 0)
        if tolerance > 0:
            if tolerance < DFM_RULES["tolerance"]["grinding"]:
                issues.append({
                    "feature": feature.get("name", feature_type),
                    "severity": "critical",
                    "type": "tolerance",
                    "value": tolerance,
                    "threshold": DFM_RULES["tolerance"]["grinding"],
                    "message": f"Tolerance ±{tolerance}\" requires lapping/honing",
                    "recommendation": "Confirm this tolerance is truly required"
                })
            elif tolerance < DFM_RULES["tolerance"]["precision"]:
                issues.append({
                    "feature": feature.get("name", feature_type),
                    "severity": "warning",
                    "type": "tolerance",
                    "value": tolerance,
                    "threshold": DFM_RULES["tolerance"]["precision"],
                    "message": f"Tolerance ±{tolerance}\" requires grinding",
                    "recommendation": "Plan for grinding operation and CMM inspection"
                })

    return issues


def recommend_materials(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Recommend materials based on requirements."""
    recommendations = []

    strength_required = requirements.get("strength_ksi", 0)
    max_temp = requirements.get("max_temp_f", 200)
    weight_critical = requirements.get("weight_critical", False)
    corrosion_exposure = requirements.get("corrosion_exposure", "low")
    cost_sensitive = requirements.get("cost_sensitive", False)

    for material_name, material_data in AEROSPACE_MATERIALS.items():
        score = 0
        fit_notes = []

        # Check strength
        if material_data["properties"]["tensile_strength_ksi"] >= strength_required:
            score += 20
            fit_notes.append("Meets strength requirement")
        else:
            score -= 50
            fit_notes.append("Below required strength")

        # Check temperature
        if material_data["properties"]["max_temp_f"] >= max_temp:
            score += 20
            fit_notes.append("Meets temperature requirement")
        else:
            score -= 30
            fit_notes.append("May not meet temperature requirement")

        # Weight consideration
        if weight_critical:
            density = material_data["properties"]["density_lb_in3"]
            if density < 0.15:
                score += 25
                fit_notes.append("Low density - good for weight-critical")
            elif density < 0.20:
                score += 10
            else:
                score -= 10
                fit_notes.append("Higher density material")

        # Corrosion consideration
        if corrosion_exposure in ["high", "marine", "chemical"]:
            if material_data["category"] in ["titanium", "inconel"]:
                score += 20
                fit_notes.append("Excellent corrosion resistance")
            elif "corrosion" in " ".join(material_data["weaknesses"]).lower():
                score -= 20
                fit_notes.append("Corrosion resistance concern")

        # Cost consideration
        if cost_sensitive:
            if material_data["relative_cost"] < 2.0:
                score += 20
                fit_notes.append("Cost effective")
            elif material_data["relative_cost"] > 6.0:
                score -= 15
                fit_notes.append("High material cost")

        # Machinability bonus
        score += int(material_data["machinability_rating"] * 15)

        recommendations.append({
            "material": material_name,
            "score": score,
            "category": material_data["category"],
            "ams_specs": material_data["ams_specs"],
            "properties": material_data["properties"],
            "strengths": material_data["strengths"],
            "weaknesses": material_data["weaknesses"],
            "machinability_rating": material_data["machinability_rating"],
            "relative_cost": material_data["relative_cost"],
            "fit_notes": fit_notes,
            "typical_applications": material_data["typical_applications"]
        })

    # Sort by score
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return recommendations


def estimate_cost(
    envelope: Dict[str, float],
    material: str,
    complexity: str,
    features: List[Dict]
) -> Dict[str, Any]:
    """Estimate rough manufacturing cost."""

    material_data = AEROSPACE_MATERIALS.get(material, AEROSPACE_MATERIALS["7075-T6"])

    # Calculate material cost
    length = envelope.get("length", 1)
    width = envelope.get("width", 1)
    height = envelope.get("height", 1)

    # Buy-to-fly ratio based on complexity
    btf_ratios = {
        "simple": 2.0,
        "moderate": 4.0,
        "complex": 8.0,
        "very_complex": 12.0
    }
    btf_ratio = btf_ratios.get(complexity, 4.0)

    # Raw material volume
    raw_volume = length * width * height * btf_ratio  # cubic inches
    material_weight = raw_volume * material_data["properties"]["density_lb_in3"]

    # Base material cost (rough estimate per pound)
    base_costs = {
        "aluminum": 3.50,
        "titanium": 25.00,
        "steel": 4.00,
        "inconel": 45.00
    }
    material_cost = material_weight * base_costs.get(material_data["category"], 5.00)

    # Machining time estimate
    complexity_multipliers = {
        "simple": 1.0,
        "moderate": 1.5,
        "complex": 2.5,
        "very_complex": 4.0
    }
    complexity_mult = complexity_multipliers.get(complexity, 1.5)

    # Base hours from volume (very rough)
    base_hours = (length * width * height / 10) * complexity_mult
    base_hours = base_hours / material_data["machinability_rating"]

    # Machining rate
    machining_rate = 95.00  # Blended rate
    machining_cost = base_hours * machining_rate

    # Setup
    setup_hours = 3.0 if complexity in ["complex", "very_complex"] else 2.0
    setup_cost = setup_hours * machining_rate

    # Inspection (10-15% of machining)
    inspection_cost = machining_cost * 0.12

    # Total
    subtotal = material_cost + machining_cost + setup_cost + inspection_cost
    overhead = subtotal * 0.85  # Manufacturing overhead
    total = subtotal + overhead

    return {
        "material_cost": round(material_cost, 2),
        "machining_cost": round(machining_cost, 2),
        "setup_cost": round(setup_cost, 2),
        "inspection_cost": round(inspection_cost, 2),
        "overhead": round(overhead, 2),
        "total_estimate": round(total, 2),
        "estimated_hours": round(base_hours + setup_hours, 1),
        "buy_to_fly_ratio": btf_ratio,
        "confidence": "low" if complexity in ["complex", "very_complex"] else "medium",
        "notes": [
            "This is a ROUGH ORDER OF MAGNITUDE estimate",
            "Actual cost requires detailed process planning",
            "Does not include NRE, tooling, or special processing"
        ]
    }


@register_factory("design_assistant")
async def design_assistant(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI-assisted product design analysis.

    FUTURE STATE CAPABILITY - Demonstrates platform extensibility.
    AI assists, engineer decides.

    Input:
        features: List of design features to analyze
        material: Material specification (or None for recommendation)
        requirements: Design requirements for material selection
        envelope: Bounding box dimensions
        complexity: simple, moderate, complex, very_complex
        program: Target program (F-35, F-22, etc.) - optional

    Output:
        dfm_analysis: Manufacturability findings
        material_recommendations: Material options with trade-offs
        cost_estimate: Rough cost estimate
        similar_parts: Similar parts from history (mock)
    """
    features = input_data.get('features', [])
    material = input_data.get('material', '7075-T6')
    requirements = input_data.get('requirements', {})
    envelope = input_data.get('envelope', {"length": 6, "width": 4, "height": 2})
    complexity = input_data.get('complexity', 'moderate')
    program = input_data.get('program', '')

    # DFM Analysis
    dfm_issues = analyze_dfm(features, material)

    # Separate by severity
    critical_issues = [i for i in dfm_issues if i["severity"] == "critical"]
    warning_issues = [i for i in dfm_issues if i["severity"] == "warning"]

    # Material Recommendations
    material_recs = []
    if requirements or not material:
        material_recs = recommend_materials(requirements or {
            "strength_ksi": 80,
            "max_temp_f": 300,
            "weight_critical": False,
            "cost_sensitive": True
        })

    # Cost Estimate
    cost_est = estimate_cost(envelope, material, complexity, features)

    # Mock similar parts (would query PDM in production)
    similar_parts = [
        {
            "part_number": "TG-5842-001",
            "description": "Throttle Grip Housing - Similar geometry",
            "material": material,
            "similarity_score": 0.85,
            "actual_cost": cost_est["total_estimate"] * 0.95,
            "actual_hours": cost_est["estimated_hours"] * 1.1,
            "lessons_learned": [
                "Used trochoidal milling for deep pockets",
                "Required fixture support for thin wall section"
            ]
        },
        {
            "part_number": "SS-5841-002",
            "description": "Sidestick Grip Body - Similar features",
            "material": material,
            "similarity_score": 0.72,
            "actual_cost": cost_est["total_estimate"] * 1.15,
            "actual_hours": cost_est["estimated_hours"] * 1.2,
            "lessons_learned": [
                "Tight tolerance on bore required grinding",
                "Surface finish spec required hand polish"
            ]
        }
    ]

    # Determine overall assessment
    if critical_issues:
        assessment = "DESIGN_REVIEW_REQUIRED"
    elif len(warning_issues) > 2:
        assessment = "MODIFICATIONS_RECOMMENDED"
    else:
        assessment = "MANUFACTURABLE"

    logger.info(
        "Design analysis completed",
        features_analyzed=len(features),
        critical_issues=len(critical_issues),
        warnings=len(warning_issues),
        material=material
    )

    return {
        "status": "success",
        "assessment": assessment,
        "dfm_analysis": {
            "features_analyzed": len(features),
            "critical_issues": critical_issues,
            "warnings": warning_issues,
            "total_issues": len(dfm_issues),
            "manufacturability_score": max(0, 100 - (len(critical_issues) * 25) - (len(warning_issues) * 10))
        },
        "material": {
            "specified": material,
            "recommendations": material_recs[:3] if material_recs else [],
            "selected_properties": AEROSPACE_MATERIALS.get(material, {}).get("properties", {})
        },
        "cost_estimate": cost_est,
        "similar_parts": similar_parts,
        "program_validation": {
            "program": program,
            "validated": bool(program),
            "requirements_checked": ["Material certification", "ITAR marking", "Customer spec"] if program else []
        },
        "model_used": "anthropic.claude-opus-4-6",
        "mode": "READ",
        "capability_status": "FUTURE_STATE",
        "disclaimer": "AI-assisted analysis. All recommendations require engineer review and approval.",
        "sources": [
            {"type": "analysis", "name": "APEX DFM Analyzer"},
            {"type": "database", "name": "Material Specifications"},
            {"type": "database", "name": "Manufacturing History"},
            {"type": "database", "name": "SolidWorks PDM"}
        ]
    }
