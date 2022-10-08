from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    title: str = Field(default=..., description="News title", example="Самый настоящий заголовок")


class PipelineResponse(BaseModel):
    is_valid: bool = Field(default=..., description="Indicates if title relates to news", example=True)
