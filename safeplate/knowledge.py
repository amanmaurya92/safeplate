"""
SafePlate Clinical & Culinary Knowledge Base:
- SIGHI Histamine Compatibility Database (Scale 0 to 3)
- Celiac / Gluten-Free Verification Data
- Dairy & Common Allergen Lookup
- Curated Safe Replacement Recipes & Ratios
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class IngredientProfile(BaseModel):
    name: str
    sighi_score: int  # 0: Well tolerated, 1: Minor/Moderately tolerated, 2: Incompatible, 3: Very Incompatible
    is_gluten: bool
    is_dairy: bool
    is_histamine_liberator: bool = False
    is_dao_blocker: bool = False
    notes: str = ""
    safe_substitutes: List[str] = []


# Standardized Ingredient Database based on clinical food intolerance indices
INGREDIENT_DATABASE: Dict[str, IngredientProfile] = {
    # Dairy & Fermented (High Histamine / Allergen)
    "parmesan": IngredientProfile(
        name="parmesan",
        sighi_score=2,
        is_gluten=False,
        is_dairy=True,
        notes="Aged cheese: extremely high in histamine and contains dairy casein.",
        safe_substitutes=["toasted pumpkin seeds + nutritional yeast (unfortified)", "hemp seed crumbles with sea salt"],
    ),
    "cheddar": IngredientProfile(
        name="cheddar",
        sighi_score=2,
        is_gluten=False,
        is_dairy=True,
        notes="Aged cheese high in biogenic amines.",
        safe_substitutes=["fresh young mozzarella (if dairy tolerated)", "grated macadamia crumble with garlic powder"],
    ),
    "cow_milk": IngredientProfile(
        name="cow_milk",
        sighi_score=1,
        is_gluten=False,
        is_dairy=True,
        notes="Contains lactose and dairy proteins.",
        safe_substitutes=["coconut milk", "fresh oat milk (certified gluten-free)", "tiger nut milk"],
    ),
    "heavy_cream": IngredientProfile(
        name="heavy_cream",
        sighi_score=1,
        is_gluten=False,
        is_dairy=True,
        notes="Dairy allergen.",
        safe_substitutes=["coconut cream", "cashew cream (freshly soaked)"],
    ),
    "butter": IngredientProfile(
        name="butter",
        sighi_score=0,
        is_gluten=False,
        is_dairy=True,
        notes="Low histamine, but contains trace dairy protein/butterfat.",
        safe_substitutes=["extra virgin olive oil", "coconut oil", "pure ghee (if casein trace tolerated)"],
    ),

    # Gluten / Grains
    "wheat_flour": IngredientProfile(
        name="wheat_flour",
        sighi_score=0,
        is_gluten=True,
        is_dairy=False,
        notes="Strictly prohibited for Celiac disease.",
        safe_substitutes=["cassava flour", "gluten-free certified rice + tapioca blend", "arrowroot powder"],
    ),
    "soy_sauce": IngredientProfile(
        name="soy_sauce",
        sighi_score=2,
        is_gluten=True,
        is_dairy=False,
        notes="Contains wheat (gluten) and fermented soy (high histamine).",
        safe_substitutes=["coconut aminos with sea salt", "homemade salt broth reduction"],
    ),
    "breadcrumbs": IngredientProfile(
        name="breadcrumbs",
        sighi_score=0,
        is_gluten=True,
        is_dairy=False,
        notes="Gluten source.",
        safe_substitutes=["crushed certified gluten-free rice crackers", "crushed plantain chips"],
    ),

    # Nightshades & Histamine Liberators
    "tomato": IngredientProfile(
        name="tomato",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        is_histamine_liberator=True,
        notes="Potent histamine liberator; can trigger severe mast cell activation.",
        safe_substitutes=["nomato sauce (beetroot, carrot, and sweet potato purée with garlic)"],
    ),
    "spinach": IngredientProfile(
        name="spinach",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        notes="High in histamine and oxalic acid.",
        safe_substitutes=["fresh baby kale", "arugula (rocket)", "bok choy"],
    ),
    "avocado": IngredientProfile(
        name="avocado",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        is_histamine_liberator=True,
        notes="High histamine and biogenic amine content.",
        safe_substitutes=["fresh zucchini purée with olive oil and lime", "cucumber ribbons"],
    ),
    "lemon_juice": IngredientProfile(
        name="lemon_juice",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        is_histamine_liberator=True,
        notes="Citrus fruits liberate histamine and irritate mucosa.",
        safe_substitutes=["distilled white vinegar (trace)", "ascorbic acid dissolved in water", "pomegranate molasses"],
    ),

    # Meat & Broths
    "bone_broth": IngredientProfile(
        name="bone_broth",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        notes="Long-simmered bone broth accumulates dangerous levels of free histamine.",
        safe_substitutes=["fresh meat broth simmered under 45 minutes", "fresh vegetable broth"],
    ),
    "bacon": IngredientProfile(
        name="bacon",
        sighi_score=2,
        is_gluten=False,
        is_dairy=False,
        notes="Cured, smoked pork with nitrates and high biogenic amines.",
        safe_substitutes=["freshly cooked chicken breast crisps", "toasted coconut flakes with smoked sea salt"],
    ),

    # Safe Staples (Score 0)
    "chicken_breast": IngredientProfile(
        name="chicken_breast",
        sighi_score=0,
        is_gluten=False,
        is_dairy=False,
        notes="Very safe when fresh or frozen immediately after slaughter.",
        safe_substitutes=[],
    ),
    "rice": IngredientProfile(
        name="rice",
        sighi_score=0,
        is_gluten=False,
        is_dairy=False,
        notes="Naturally gluten-free and low histamine.",
        safe_substitutes=[],
    ),
    "olive_oil": IngredientProfile(
        name="olive_oil",
        sighi_score=0,
        is_gluten=False,
        is_dairy=False,
        notes="Extra virgin olive oil is well tolerated.",
        safe_substitutes=[],
    ),
    "zucchini": IngredientProfile(
        name="zucchini",
        sighi_score=0,
        is_gluten=False,
        is_dairy=False,
        notes="Gentle, low-histamine vegetable.",
        safe_substitutes=[],
    ),
    "garlic": IngredientProfile(
        name="garlic",
        sighi_score=0,
        is_gluten=False,
        is_dairy=False,
        notes="Well tolerated for histamine in moderate amounts.",
        safe_substitutes=[],
    ),
}
