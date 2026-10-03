"""
SafePlate Agent Engine:
Multi-step intelligent recipe verification and substitution agent
instrumented with Sentry Agent Tracing.
"""

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from safeplate.tools import audit_ingredient, get_safe_substitute
from safeplate.telemetry import (
    trace_agent_pipeline,
    trace_tool_call,
    trace_llm_inference,
    metrics,
)


class UserDietaryProfile(BaseModel):
    user_name: str = "Elena"
    has_celiac: bool = True
    has_dairy_allergy: bool = True
    max_sighi_histamine_score: int = 0  # 0 = Strict low-histamine


class IngredientCheck(BaseModel):
    ingredient: str
    is_safe: bool
    sighi_score: int = 0
    reasons: List[str] = Field(default_factory=list)
    chosen_substitute: Optional[str] = None


class SafeRecipeRemix(BaseModel):
    original_title: str
    safe_title: str
    safety_summary: str
    flagged_ingredients: List[IngredientCheck]
    safe_ingredients: List[str]
    cooking_instructions: List[str]
    total_latency_ms: float
    total_tokens: int
    tool_calls_count: int


class SafePlateAgent:
    def __init__(self, profile: Optional[UserDietaryProfile] = None, model_name: str = "llama-3.2-3b-instruct"):
        self.profile = profile or UserDietaryProfile()
        self.model_name = model_name

    def remix_recipe(self, title: str, ingredients: List[str], unoptimized_loop: bool = False) -> SafeRecipeRemix:
        """
        Executes the multi-step agent pipeline:
        1. Ingests and audits each ingredient against clinical constraints.
        2. Queries substitution engine for flagged allergens/histamines.
        3. (If unoptimized_loop is True: simulates redundant verification passes to demonstrate Sentry trace debugging).
        4. Synthesizes a certified allergy-safe recipe remix.
        """
        pipeline_name = f"safeplate.recipe_remix.{title.lower().replace(' ', '_')}"
        start_time = time.perf_counter()

        with trace_agent_pipeline(pipeline_name, input_prompt=f"Remix {title}", user_id=self.profile.user_name):
            flagged: List[IngredientCheck] = []
            safe_list: List[str] = []

            # Step 1 & 2: Audit ingredients
            for ing in ingredients:
                audit = audit_ingredient(
                    ingredient=ing,
                    check_celiac=self.profile.has_celiac,
                    check_dairy=self.profile.has_dairy_allergy,
                    max_sighi=self.profile.max_sighi_histamine_score,
                )

                if audit["is_safe"]:
                    safe_list.append(ing)
                else:
                    sub_info = get_safe_substitute(ing)
                    chosen_sub = sub_info["substitutes"][0] if sub_info["substitutes"] else "safe alternative"
                    
                    # Demonstration of unoptimized loop for Sentry trace contrast:
                    if unoptimized_loop:
                        # Re-auditing multiple times without caching
                        for _ in range(3):
                            time.sleep(0.04) # simulated redundant network/DB roundtrip
                            audit_ingredient(ing, self.profile.has_celiac, self.profile.has_dairy_allergy, self.profile.max_sighi_histamine_score)

                    flagged.append(IngredientCheck(
                        ingredient=ing,
                        is_safe=False,
                        sighi_score=audit.get("sighi_score", 2),
                        reasons=audit["reasons"],
                        chosen_substitute=chosen_sub,
                    ))
                    safe_list.append(f"{chosen_sub} (replacing {ing})")

            # Step 3: LLM Synthesis with token accounting
            prompt_tokens = 450 + len(ingredients) * 45
            completion_tokens = 320
            if unoptimized_loop:
                # Bloated unoptimized prompt with redundant context
                prompt_tokens += 1800

            with trace_llm_inference(
                model=self.model_name,
                prompt=f"Generate safe recipe for {self.profile.user_name} based on verified ingredients",
                temperature=0.2,
                estimated_prompt_tokens=prompt_tokens,
                estimated_completion_tokens=completion_tokens,
                cost_usd=0.0, # Open-weights local model = $0.00
            ):
                # Generates deterministic structured cooking instructions
                instructions = [
                    f"Heat cold-pressed olive oil in a non-reactive stainless steel pan over medium heat.",
                    f"Sear fresh chicken breast for 6-8 minutes until golden and thoroughly cooked (avoiding high-histamine browning).",
                    f"Add {' and '.join([f.chosen_substitute or f.ingredient for f in flagged[:2]])} along with fresh zucchini.",
                    f"Simmer gently for 10 minutes. Serve immediately (do not store as leftovers to prevent histamine accumulation).",
                ]

            total_duration_ms = (time.perf_counter() - start_time) * 1000

            return SafeRecipeRemix(
                original_title=title,
                safe_title=f"Elena-Safe {title} (Gluten-Free & Low-Histamine)",
                safety_summary=f"Audit complete: {len(flagged)} allergens/histamine triggers replaced with clinical substitutes.",
                flagged_ingredients=flagged,
                safe_ingredients=safe_list,
                cooking_instructions=instructions,
                total_latency_ms=round(total_duration_ms, 2),
                total_tokens=prompt_tokens + completion_tokens,
                tool_calls_count=metrics.tool_calls_count,
            )
