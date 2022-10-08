from typing import List, Optional

from service_insights.factory import load_sentiment_model, load_spacy_pipeline
from service_insights.models import (
    PipelineItemResponse,
    PipelineRequest,
    PipelineResponse,
    Sentiment,
)
from service_insights.settings import Settings


class Pipeline:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.spacy_model = load_spacy_pipeline()
        self.sentiment_model = load_sentiment_model()

    def run(self, request: PipelineRequest) -> PipelineResponse:
        items: List[PipelineItemResponse] = []
        original_text = request.text
        original_text = (
            request.text.replace("см.", "см")
            .replace("тп.", "тп")
            .replace("др.", "др")
            .replace("тд.", "тд")
            .replace("след.", "след")
        )
        for sentence in self.spacy_model(original_text).sents:
            prediction = self.sentiment_model.predict([sentence.text], k=10)[0]
            if prediction["positive"] >= prediction["negative"]:
                score = prediction["positive"]
                sentiment = Sentiment.positive
            else:
                score = prediction["negative"]
                sentiment = Sentiment.negative
            items.append(
                PipelineItemResponse(
                    start=sentence.start_char,
                    end=sentence.end_char,
                    score=score,
                    sentiment=sentiment,
                    text=original_text[sentence.start_char : sentence.end_char],
                )
            )
        return PipelineResponse(items=items)
