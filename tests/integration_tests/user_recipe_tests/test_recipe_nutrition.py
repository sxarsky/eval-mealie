from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_nutrition import Nutrition
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_recipe(unique_user: TestUser, **kwargs) -> Recipe:
    return unique_user.repos.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string(10), **kwargs)
    )


def test_nutrition_summary_totals_and_per_serving(api_client: TestClient, unique_user: TestUser):
    recipe = _create_recipe(
        unique_user,
        recipe_servings=4,
        nutrition=Nutrition(calories="480", protein_content="22 g", fat_content="13g", sodium_content="800 mg"),
    )

    response = api_client.get(api_routes.recipes_slug_nutrition(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    summary = response.json()

    assert summary["recipeId"] == str(recipe.id)
    assert summary["slug"] == recipe.slug
    assert summary["servings"] == 4
    assert summary["hasNutrition"] is True

    assert summary["total"]["calories"] == 480
    assert summary["total"]["proteinContent"] == 22
    assert summary["total"]["fatContent"] == 13
    assert summary["total"]["sodiumContent"] == 800
    assert summary["total"]["sugarContent"] is None

    assert summary["perServing"]["calories"] == 120
    assert summary["perServing"]["proteinContent"] == 5.5
    assert summary["perServing"]["fatContent"] == 3.25
    assert summary["perServing"]["sodiumContent"] == 200
    assert summary["perServing"]["sugarContent"] is None


def test_nutrition_summary_without_servings(api_client: TestClient, unique_user: TestUser):
    recipe = _create_recipe(unique_user, nutrition=Nutrition(calories="300"))

    response = api_client.get(api_routes.recipes_slug_nutrition(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    summary = response.json()

    assert summary["servings"] == 0
    assert summary["hasNutrition"] is True
    assert summary["total"]["calories"] == 300
    assert summary["perServing"] is None


def test_nutrition_summary_without_nutrition(api_client: TestClient, unique_user: TestUser):
    recipe = _create_recipe(unique_user, recipe_servings=2)

    response = api_client.get(api_routes.recipes_slug_nutrition(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    summary = response.json()

    assert summary["hasNutrition"] is False
    assert all(value is None for value in summary["total"].values())
    assert all(value is None for value in summary["perServing"].values())


def test_nutrition_summary_by_id(api_client: TestClient, unique_user: TestUser):
    recipe = _create_recipe(unique_user, nutrition=Nutrition(calories="100"))

    response = api_client.get(api_routes.recipes_slug_nutrition(str(recipe.id)), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["slug"] == recipe.slug


def test_nutrition_summary_not_found(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.recipes_slug_nutrition(random_string()), headers=unique_user.token)
    assert response.status_code == 404
