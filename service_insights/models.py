from typing import List
from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    text: str = Field(default=..., description="Text of the news article", example="Арбузы подорожали")


class PipelineItemResponse(BaseModel):
    start: int = Field(default=..., description="Start index of the insight", example=0)
    end: int = Field(default=..., description="Last index of the insight that is not included", example=5)


class PipelineResponse(BaseModel):
    items: List[PipelineItemResponse] = Field(default=..., description="List of start and end indices of the insights",
                                              example=[PipelineItemResponse(start=0, end=9),
                                                       PipelineItemResponse(start=56, end=98)])
