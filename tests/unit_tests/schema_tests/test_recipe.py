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
    ["prep_time", "cook_time", "perform_time", "total_time", "expected_count"],
    [
        (None, None, None, None, 0),
        ("30 minutes", None, None, None, 1),
        ("30 minutes", "45 minutes", None, None, 2),
        ("30 minutes", "45 minutes", "15 minutes", "1h30min", 4),
        ("", None, None, None, 1),
    ],
)
def test_time_fields_count(
    prep_time: str | None,
    cook_time: str | None,
    perform_time: str | None,
    total_time: str | None,
    expected_count: int,
):
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        prep_time=prep_time,
        cook_time=cook_time,
        perform_time=perform_time,
        total_time=total_time,
    )
    assert recipe.time_fields_count == expected_count
