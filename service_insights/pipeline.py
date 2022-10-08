from typing import List, Optional

from service_insights.factory import load_sentiment_model, load_spacy_pipeline
from service_insights.models import (
    PipelineItemResponse,
    PipelineItemTextResponse,
    PipelineRequest,
    PipelineResponse,
)
from service_insights.settings import Settings


class Pipeline:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.spacy_model = load_spacy_pipeline()
        self.sentiment_model = load_sentiment_model()

    def run(self, request: PipelineRequest) -> PipelineResponse:
        items: List[PipelineItemResponse] = []
        items_text: List[PipelineItemTextResponse] = []
        for sentence in self.spacy_model(request.text).sents:
            prediction = self.sentiment_model.predict([sentence.text], k=10)[0]
            if prediction["positive"] >= self.settings.positive_sentiment_threshold:
                items.append(
                    PipelineItemResponse(
                        start=sentence.start_char, end=sentence.end_char
                    )
                )
                items_text.append(
                    PipelineItemTextResponse(
                        text=request.text[sentence.start_char : sentence.end_char]
                    )
                )
            elif prediction["negative"] >= self.settings.negative_sentiment_threshold:
                items.append(
                    PipelineItemResponse(
                        start=sentence.start_char, end=sentence.end_char
                    )
                )
                items_text.append(
                    PipelineItemTextResponse(
                        text=request.text[sentence.start_char : sentence.end_char]
                    )
                )

        return PipelineResponse(items=items, items_text=items_text)
