from fastapi.testclient import TestClient

from mealie.schema.household.group_shopping_list import ShoppingListAddRecipeParamsBulk
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientFood
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_list(api_client: TestClient, unique_user: TestUser) -> str:
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    assert response.status_code == 201
    return response.json()["id"]


def _add_recipe(api_client: TestClient, unique_user: TestUser, list_id: str, recipe: Recipe, scale: float) -> dict:
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe(list_id),
        json=utils.jsonify(
            [ShoppingListAddRecipeParamsBulk(recipe_id=recipe.id, recipe_increment_quantity=scale).model_dump()]
        ),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.households_shopping_lists_item_id(list_id), headers=unique_user.token)
    return utils.assert_deserialize(response, 200)


def test_recipe_quantities_are_rounded_to_two_decimals(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos
    flour = database.ingredient_foods.create(SaveIngredientFood(name=random_string(), group_id=unique_user.group_id))
    sugar = database.ingredient_foods.create(SaveIngredientFood(name=random_string(), group_id=unique_user.group_id))
    recipe = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(10),
            recipe_ingredient=[
                RecipeIngredient(quantity=1 / 3, food=flour),
                RecipeIngredient(quantity=0.125, food=sugar),
            ],
        )
    )

    list_id = _create_list(api_client, unique_user)
    shopping_list = _add_recipe(api_client, unique_user, list_id, recipe, scale=2)

    quantities = {item["foodId"]: item["quantity"] for item in shopping_list["listItems"]}
    assert quantities[str(flour.id)] == 0.67
    assert quantities[str(sugar.id)] == 0.25

    # the recipe reference keeps the unrounded recipe quantity so later scale changes stay exact
    for item in shopping_list["listItems"]:
        assert item["recipeReferences"][0]["recipeScale"] == 2


def test_recipe_quantities_rounding_keeps_whole_numbers(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos
    eggs = database.ingredient_foods.create(SaveIngredientFood(name=random_string(), group_id=unique_user.group_id))
    recipe = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(10),
            recipe_ingredient=[RecipeIngredient(quantity=3, food=eggs)],
        )
    )

    list_id = _create_list(api_client, unique_user)
    shopping_list = _add_recipe(api_client, unique_user, list_id, recipe, scale=1.5)

    assert len(shopping_list["listItems"]) == 1
    assert shopping_list["listItems"][0]["quantity"] == 4.5
