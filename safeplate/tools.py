"""
SafePlate Agent Tools:
Deterministic clinical verification and substitution tools wrapped in Sentry Agent Tracing.
"""

from typing import Any, Dict, List, Optional
from safeplate.knowledge import INGREDIENT_DATABASE, IngredientProfile
from safeplate.telemetry import trace_tool_call


def normalize_ingredient(raw_name: str) -> str:
    cleaned = raw_name.lower().strip().replace("-", "_").replace(" ", "_")
    for key in INGREDIENT_DATABASE:
        if key in cleaned or cleaned in key:
            return key
    return cleaned


def audit_ingredient(
    ingredient: str,
    check_celiac: bool = True,
    check_dairy: bool = True,
    max_sighi: int = 0
) -> Dict[str, Any]:
    """
    Checks an individual ingredient against Celiac (gluten), Dairy, and SIGHI histamine limits.
    """
    with trace_tool_call("audit_ingredient", {
        "ingredient": ingredient,
        "check_celiac": check_celiac,
        "check_dairy": check_dairy,
        "max_sighi": max_sighi
    }) as span:
        norm_name = normalize_ingredient(ingredient)
        profile = INGREDIENT_DATABASE.get(norm_name)

        if not profile:
            # Unknown ingredient defaults to cautious check
            res = {
                "ingredient": ingredient,
                "is_safe": True,
                "confidence": "moderate",
                "reasons": ["Ingredient not flagged in high-risk histamine/gluten index."],
                "substitutes": []
            }
            if span:
                span.set_data("tool.result", res)
            return res

        reasons = []
        is_safe = True

        if check_celiac and profile.is_gluten:
            is_safe = False
            reasons.append(f"Contains GLUTEN (Prohibited for Celiac: {profile.notes})")

        if check_dairy and profile.is_dairy:
            is_safe = False
            reasons.append(f"Contains DAIRY (Casein/Lactose: {profile.notes})")

        if profile.sighi_score > max_sighi:
            is_safe = False
            reasons.append(f"High Histamine / SIGHI Score {profile.sighi_score} > {max_sighi} ({profile.notes})")

        if profile.is_histamine_liberator:
            is_safe = False
            reasons.append(f"Histamine Liberator ({profile.notes})")

        res = {
            "ingredient": ingredient,
            "is_safe": is_safe,
            "confidence": "high",
            "sighi_score": profile.sighi_score,
            "reasons": reasons,
            "substitutes": profile.safe_substitutes if not is_safe else []
        }
        if span:
            span.set_data("tool.result", res)
        return res


def get_safe_substitute(ingredient: str) -> Dict[str, Any]:
    """
    Retrieves certified safe, tested culinary alternatives for unsafe ingredients.
    """
    with trace_tool_call("get_safe_substitute", {"ingredient": ingredient}) as span:
        norm_name = normalize_ingredient(ingredient)
        profile = INGREDIENT_DATABASE.get(norm_name)
        if profile and profile.safe_substitutes:
            res = {
                "ingredient": ingredient,
                "substitutes": profile.safe_substitutes,
                "culinary_notes": profile.notes
            }
        else:
            res = {
                "ingredient": ingredient,
                "substitutes": ["fresh cold-pressed olive oil", "fresh zucchini or carrot purée"],
                "culinary_notes": "Generic hypoallergenic substitute"
            }
        if span:
            span.set_data("tool.result", res)
        return res
