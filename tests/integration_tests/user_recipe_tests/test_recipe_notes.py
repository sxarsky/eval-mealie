import json

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_notes import RECIPE_NOTE_TEXT_MAX_LENGTH
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_recipe(api_client: TestClient, unique_user: TestUser) -> dict:
    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    slug = json.loads(response.text)

    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 200
    return json.loads(response.text)


@pytest.mark.parametrize("use_patch", [True, False])
def test_recipe_notes_accept_text_at_limit(api_client: TestClient, unique_user: TestUser, use_patch: bool):
    recipe = _create_recipe(api_client, unique_user)
    recipe_url = api_routes.recipes_slug(recipe["slug"])

    notes = [
        {"title": "Short", "text": "a short note"},
        {"title": "At limit", "text": "x" * RECIPE_NOTE_TEXT_MAX_LENGTH},
    ]
    recipe["notes"] = notes

    if use_patch:
        response = api_client.patch(recipe_url, json=recipe, headers=unique_user.token)
    else:
        response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    assert json.loads(response.text)["notes"] == notes


@pytest.mark.parametrize("use_patch", [True, False])
def test_recipe_notes_reject_text_over_limit(api_client: TestClient, unique_user: TestUser, use_patch: bool):
    recipe = _create_recipe(api_client, unique_user)
    recipe_url = api_routes.recipes_slug(recipe["slug"])

    original_notes = [{"title": "Keep me", "text": "original note"}]
    recipe["notes"] = original_notes
    response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    recipe["notes"] = [
        {"title": "Fine", "text": "ok"},
        {"title": "Too long", "text": "x" * (RECIPE_NOTE_TEXT_MAX_LENGTH + 1)},
    ]
    if use_patch:
        response = api_client.patch(recipe_url, json=recipe, headers=unique_user.token)
    else:
        response = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert response.status_code == 422

    # nothing from the rejected request is persisted
    response = api_client.get(recipe_url, headers=unique_user.token)
    assert response.status_code == 200
    assert json.loads(response.text)["notes"] == original_notes
