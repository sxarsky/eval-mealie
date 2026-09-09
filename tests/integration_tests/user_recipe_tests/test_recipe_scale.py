import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientFood, SaveIngredientUnit
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def recipe_with_ingredients(api_client: TestClient, unique_user: TestUser) -> dict:
    """
    A recipe with a mix of ingredient shapes, read back through the API. Unit and food names are
    randomised because they are unique per group and the user fixture is shared across tests.
    """
    database = unique_user.repos

    cup_name = random_string(6)
    gram_name = random_string(6)
    cup = database.ingredient_units.create(
        SaveIngredientUnit(name=cup_name, group_id=unique_user.group_id, fraction=True)
    )
    gram = database.ingredient_units.create(
        SaveIngredientUnit(name=gram_name, plural_name=f"{gram_name}s", group_id=unique_user.group_id, fraction=False)
    )
    flour = database.ingredient_foods.create(SaveIngredientFood(name=random_string(6), group_id=unique_user.group_id))
    salt = database.ingredient_foods.create(SaveIngredientFood(name=random_string(6), group_id=unique_user.group_id))

    recipe = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(10),
            recipe_ingredient=[
                RecipeIngredient(quantity=2, note="eggs"),
                RecipeIngredient(quantity=0.5, unit=cup, food=flour),
                RecipeIngredient(quantity=1.5, unit=gram, food=salt),
                RecipeIngredient(quantity=None, note="pepper to taste"),
            ],
        )
    )

    response = api_client.get(api_routes.recipes_slug(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    data = response.json()
    data["_names"] = {"cup": cup.name, "gram": gram.name, "flour": flour.name, "salt": salt.name}
    return data


def test_scale_recipe_ingredients(api_client: TestClient, unique_user: TestUser, recipe_with_ingredients: dict):
    slug = recipe_with_ingredients["slug"]
    names = recipe_with_ingredients["_names"]

    response = api_client.get(api_routes.recipes_slug_scale(slug), params={"factor": 2}, headers=unique_user.token)
    assert response.status_code == 200
    scaled = response.json()

    assert scaled["slug"] == slug
    quantities = [ingredient["quantity"] for ingredient in scaled["recipeIngredient"]]
    assert quantities == [4, 1, 3, None]

    # display text is rebuilt from the scaled quantities
    displays = [ingredient["display"] for ingredient in scaled["recipeIngredient"]]
    assert displays[0] == "4 eggs"
    assert displays[1] == f"1 {names['cup']} {names['flour']}"
    assert displays[2] == f"3 {names['gram']}s {names['salt']}"
    assert displays[3] == "pepper to taste"


def test_scale_recipe_fractional_factor(api_client: TestClient, unique_user: TestUser, recipe_with_ingredients: dict):
    slug = recipe_with_ingredients["slug"]

    response = api_client.get(api_routes.recipes_slug_scale(slug), params={"factor": 0.5}, headers=unique_user.token)
    assert response.status_code == 200
    scaled = response.json()

    quantities = [ingredient["quantity"] for ingredient in scaled["recipeIngredient"]]
    assert quantities == [1, 0.25, 0.75, None]
    assert scaled["recipeIngredient"][0]["display"] == "1 eggs"


def test_scale_recipe_does_not_modify_stored_recipe(
    api_client: TestClient, unique_user: TestUser, recipe_with_ingredients: dict
):
    slug = recipe_with_ingredients["slug"]

    response = api_client.get(api_routes.recipes_slug_scale(slug), params={"factor": 3}, headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 200
    stored = response.json()
    assert stored["recipeIngredient"] == recipe_with_ingredients["recipeIngredient"]


@pytest.mark.parametrize("factor", [0, -1, "abc"])
def test_scale_recipe_invalid_factor(
    api_client: TestClient, unique_user: TestUser, recipe_with_ingredients: dict, factor
):
    slug = recipe_with_ingredients["slug"]
    response = api_client.get(api_routes.recipes_slug_scale(slug), params={"factor": factor}, headers=unique_user.token)
    assert response.status_code == 422


def test_scale_recipe_missing_factor(api_client: TestClient, unique_user: TestUser, recipe_with_ingredients: dict):
    slug = recipe_with_ingredients["slug"]
    response = api_client.get(api_routes.recipes_slug_scale(slug), headers=unique_user.token)
    assert response.status_code == 422


def test_scale_recipe_not_found(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(
        api_routes.recipes_slug_scale(random_string()), params={"factor": 2}, headers=unique_user.token
    )
    assert response.status_code == 404
