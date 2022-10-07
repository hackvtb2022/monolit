from typing import Optional, List
from service_insights.settings import Settings
from service_insights.factory import load_sentiment_model, load_spacy_pipeline
from service_insights.models import PipelineRequest, PipelineItemResponse, PipelineResponse


class Pipeline:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.spacy_model = load_spacy_pipeline()
        self.sentiment_model = load_sentiment_model()

    def run(self, request: PipelineRequest) -> PipelineResponse:
        items: List[PipelineItemResponse] = []
        for sentence in self.spacy_model(request.text).sents:
            prediction = self.sentiment_model.predict([sentence.text], k=10)[0]
            print(sentence.text, prediction)
            if prediction["positive"] >= self.settings.positive_sentiment_threshold:
                items.append(PipelineItemResponse(start=sentence.start_char, end=sentence.end_char))
            elif prediction["negative"] >= self.settings.negative_sentiment_threshold:
                items.append(PipelineItemResponse(start=sentence.start_char, end=sentence.end_char))

        return PipelineResponse(items=items)
