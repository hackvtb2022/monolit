from doctest import Example
from typing import List
from enum import Enum

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"


class PipelineRequest(BaseModel):
    text: str = Field(
        default=..., description="Text of the news article", example="Арбузы подорожали"
    )


class PipelineItemResponse(BaseModel):
    start: int = Field(default=..., description="Start index of the insight", example=0)
    end: int = Field(
        default=...,
        description="Last index of the insight that is not included",
        example=5,
    )
    sentiment: Sentiment = Field(default=...,
                                 description="Most probable sentiment between positive and negative",
                                 example=Sentiment.positive)
    score: float = Field(default=..., description="Score of the sentiment", example=0.94)


class PipelineItemTextResponse(BaseModel):
    text: str = Field(
        default=..., description="Text in range [start:end]", example="Арбузы"
    )


class PipelineResponse(BaseModel):
    items: List[PipelineItemResponse] = Field(
        default=...,
        description="List of start and end indices of the insights",
        example=[
            PipelineItemResponse(start=0, end=9, sentiment=Sentiment.positive, score=0.54),
            PipelineItemResponse(start=56, end=98, sentiment=Sentiment.negative, score=0.9),
        ],
    )
    items_text: List[PipelineItemTextResponse] = Field(
        default=...,
        description="List of text in ragne of start and end of the insights",
        example=[PipelineItemTextResponse(text="Арбузы")],
    )
