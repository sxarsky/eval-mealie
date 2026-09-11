from pydantic import BaseModel, ConfigDict, Field

RECIPE_NOTE_TEXT_MAX_LENGTH = 255
"""Maximum number of characters allowed in a single recipe note's text"""


class RecipeNote(BaseModel):
    title: str
    text: str = Field(max_length=RECIPE_NOTE_TEXT_MAX_LENGTH)
    model_config = ConfigDict(from_attributes=True)
