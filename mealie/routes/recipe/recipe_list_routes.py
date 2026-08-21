from uuid import UUID

import orjson
from fastapi import Depends, HTTPException, Query, Request
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.response.pagination import RecipeSearchQuery

from ._base import BaseRecipeController, JSONBytes

router = UserAPIRouter(prefix="/recipes")


@controller(router)
class RecipeListController(BaseRecipeController):
    @router.get("", response_model=PaginationBase[RecipeSummary])
    def get_all(
        self,
        request: Request,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search_query: RecipeSearchQuery = Depends(make_dependable(RecipeSearchQuery)),
        categories: list[UUID4 | str] | None = Query(None),
        tags: list[UUID4 | str] | None = Query(None),
        tools: list[UUID4 | str] | None = Query(None),
        foods: list[UUID4 | str] | None = Query(None),
        households: list[UUID4 | str] | None = Query(None),
        categories_only: bool = Query(False, description="When true, return only recipes that have at least one category"),
    ):
        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            if isinstance(search_query.cookbook, UUID):
                cb_match_attr = "id"
            else:
                try:
                    UUID(search_query.cookbook)
                    cb_match_attr = "id"
                except ValueError:
                    cb_match_attr = "slug"
            cookbook_data = self.group_cookbooks.get_one(search_query.cookbook, cb_match_attr)

            if cookbook_data is None:
                raise HTTPException(status_code=404, detail="cookbook not found")

        # We use "group_recipes" here so we can return all recipes regardless of household. The query filter can
        # include a household_id to filter by household.
        # We use "by_user" so we can sort favorites and other user-specific data correctly.
        pagination_response = self.group_recipes.by_user(self.user.id).page_all(
            pagination=q,
            cookbook=cookbook_data,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            households=households,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        if categories_only:
            pagination_response.items = [item for item in pagination_response.items if item.recipe_category]
            pagination_response.total = len(pagination_response.items)

        # merge default pagination with the request's query params
        query_params = q.model_dump() | {**request.query_params}
        pagination_response.set_pagination_guides(
            router.url_path_for("get_all"),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

