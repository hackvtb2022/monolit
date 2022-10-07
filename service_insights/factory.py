import spacy
import logging
import functools

from typing import Optional
from service_insights.settings import Settings
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel


@functools.lru_cache(1)
def load_sentiment_model() -> FastTextSocialNetworkModel:
    logging.info('Started loading sentiment model')
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    logging.info('Successfully loaded sentiment model')
    return model


@functools.lru_cache(1)
def load_spacy_pipeline(settings: Optional[Settings] = None):
    settings = settings or Settings()
    logging.info('Started loading spacy model')
    model = spacy.load(settings.spacy_model_name)
    logging.info('Successfully loaded spacy model')
    return model
