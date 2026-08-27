from typing import Any
from uuid import uuid4

import pytest

from mealie.schema.recipe import RecipeSummary

SHOULD_ERROR = "this_test_should_error"


@pytest.mark.parametrize("field", ["recipe_servings", "recipe_yield_quantity"])
@pytest.mark.parametrize(
    ["val", "expected"],
    [
        (0, 0),
        (None, 0),
        ("", 0),
        (10, 10),
        (2.25, 2.25),
        ("10", 10),
        ("invalid", SHOULD_ERROR),
    ],
)
def test_recipe_number_sanitation(field: str, val: Any, expected: Any):
    try:
        recipe = RecipeSummary(
            id=uuid4(),
            user_id=uuid4(),
            household_id=uuid4(),
            group_id=uuid4(),
            **{field: val},
        )
    except ValueError:
        if expected == SHOULD_ERROR:
            return
        else:
            raise

    assert expected != SHOULD_ERROR, "Value should have errored"
    assert getattr(recipe, field) == expected


@pytest.mark.parametrize("field", ["recipe_yield", "total_time", "prep_time", "cook_time", "perform_time"])
@pytest.mark.parametrize(
    ["val", "expected"],
    [
        ("normal string", "normal string"),
        ("", ""),
        (None, None),
        (10, "10"),
        (2.25, "2.25"),
    ],
)
def test_recipe_string_sanitation(field: str, val: Any, expected: Any):
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        **{field: val},
    )

    assert getattr(recipe, field) == expected


def test_recipe_preserves_existing_slug():
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        name="Bols nourrissants (copie de Zuppa)",
        slug="nourish-bowls-zuppa-copycat",
    )

    assert recipe.slug == "nourish-bowls-zuppa-copycat"


@pytest.mark.parametrize(
    ["time_fields", "expected_count"],
    [
        ({}, 0),
        ({"prep_time": None, "cook_time": None, "perform_time": None, "total_time": None}, 0),
        ({"prep_time": "10 minutes"}, 1),
        ({"prep_time": "10 minutes", "cook_time": "20 minutes"}, 2),
        ({"prep_time": "10 minutes", "cook_time": "20 minutes", "perform_time": "5 minutes"}, 3),
        (
            {
                "prep_time": "10 minutes",
                "cook_time": "20 minutes",
                "perform_time": "5 minutes",
                "total_time": "35 minutes",
            },
            4,
        ),
        ({"total_time": "35 minutes", "cook_time": None}, 1),
    ],
)
def test_recipe_time_fields_count(time_fields: dict[str, Any], expected_count: int):
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        **time_fields,
    )

    assert recipe.time_fields_count == expected_count

    # the field is part of the public API response, serialized under its camelCase alias
    assert recipe.model_dump(by_alias=True)["timeFieldsCount"] == expected_count
