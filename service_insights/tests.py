import pytest

from service_insights.pipeline import Pipeline
from service_insights.factory import load_sentiment_model, load_spacy_pipeline
from service_insights.models import PipelineResponse, PipelineItemResponse, PipelineRequest


def test_load_sentiment_model():
    model = load_sentiment_model()
    assert model


def test_load_spacy_pipeline():
    model = load_spacy_pipeline()
    assert model


@pytest.mark.parametrize("pipeline_request, expected", [
    (
        PipelineRequest(text="Супер классная крутая новость!"),
        PipelineResponse(items=[
            PipelineItemResponse(start=0, end=30)
        ])
    ),
    (
        PipelineRequest(text="Ужасная и отвратительная новость!"),
        PipelineResponse(items=[
            PipelineItemResponse(start=0, end=33)
        ])
    )
])
def test_pipeline(pipeline_request: PipelineRequest, expected: PipelineResponse):
    pipeline = Pipeline()
    response = pipeline.run(pipeline_request)
    assert response == expected
