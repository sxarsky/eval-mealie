from pydantic import UUID4, ConfigDict
from pydantic.alias_generators import to_camel

from mealie.schema._mealie import MealieModel


class Nutrition(MealieModel):
    calories: str | None = None
    carbohydrate_content: str | None = None
    cholesterol_content: str | None = None
    fat_content: str | None = None
    fiber_content: str | None = None
    protein_content: str | None = None
    saturated_fat_content: str | None = None
    sodium_content: str | None = None
    sugar_content: str | None = None
    trans_fat_content: str | None = None
    unsaturated_fat_content: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
    )


class NutritionValues(MealieModel):
    """Numeric nutrition values; ``None`` when the recipe does not provide the value"""

    calories: float | None = None
    carbohydrate_content: float | None = None
    cholesterol_content: float | None = None
    fat_content: float | None = None
    fiber_content: float | None = None
    protein_content: float | None = None
    saturated_fat_content: float | None = None
    sodium_content: float | None = None
    sugar_content: float | None = None
    trans_fat_content: float | None = None
    unsaturated_fat_content: float | None = None


class RecipeNutritionSummary(MealieModel):
    recipe_id: UUID4
    slug: str
    servings: float
    """the recipe's servings; per-serving values are only available when this is greater than zero"""

    has_nutrition: bool
    """true when at least one nutrition value could be read from the recipe"""

    total: NutritionValues
    """nutrition for the whole recipe, parsed to numbers"""

    per_serving: NutritionValues | None = None
    """total divided by servings, rounded to two decimals; ``None`` when servings is not set"""
