import pytest

from service_insights.pipeline import Pipeline
from service_insights.factory import load_sentiment_model, load_spacy_pipeline
from service_insights.models import PipelineResponse, PipelineItemResponse, PipelineRequest, Sentiment, PipelineItemTextResponse


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
            PipelineItemResponse(start=0, end=30, sentiment=Sentiment.positive, score=0.93)
        ], items_text=[PipelineItemTextResponse(text="Супер классная крутая новость!")])
    ),
    (
        PipelineRequest(text="Ужасная и отвратительная новость!"),
        PipelineResponse(items=[
            PipelineItemResponse(start=0, end=33, sentiment=Sentiment.negative, score=0.91)
        ], items_text=[PipelineItemTextResponse(text="Ужасная и отвратительная новость!")])
    ),
    (
        PipelineRequest(text="Что то"),
        PipelineResponse(items=[
            PipelineItemResponse(start=0, end=6, sentiment=Sentiment.positive, score=0.91)
        ], items_text=[PipelineItemTextResponse(text="Что то")])
    ),
    (
        PipelineRequest(text="Просто. Очень круто!"),
        PipelineResponse(items=[
            PipelineItemResponse(start=0, end=7, sentiment=Sentiment.negative, score=0.34),
            PipelineItemResponse(start=8, end=20, sentiment=Sentiment.positive, score=0.34)
        ], items_text=[PipelineItemTextResponse(text="Просто."), PipelineItemTextResponse(text="Очень круто!")])
    ),
])
def test_pipeline(pipeline_request: PipelineRequest, expected: PipelineResponse):
    pipeline = Pipeline()
    response = pipeline.run(pipeline_request)
    response_pairs = [(item.start, item.end, item.sentiment) for item in response.items]
    expected_pairs = [(item.start, item.end, item.sentiment) for item in expected.items]
    assert set(response_pairs) == set(expected_pairs)
