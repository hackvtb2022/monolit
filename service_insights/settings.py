from pydantic import BaseSettings


class Settings(BaseSettings):
    spacy_model_name: str = "ru_core_news_sm"
    positive_sentiment_threshold: float = 0.25
    negative_sentiment_threshold: float = 0.25

    class Config:
        env_prefix = "service_insights_"
