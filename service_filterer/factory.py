import functools
import logging
import pickle


@functools.lru_cache(1)
def load_word2norm():
    logging.info("Started loading word2norm")
    with open("/app/resources/word2norm.pickle", "rb") as f:
        word2norm_ru = pickle.load(f)
    logging.info("Successfully loaded word2norm")
    return word2norm_ru


@functools.lru_cache(1)
def load_tokens():
    logging.info("Started loading tokens")
    with open("/app/resources/tokens.txt") as f:
        tokens = {x.strip() for x in f.readlines()}
    logging.info("Successfully loaded tokens")
    return tokens


@functools.lru_cache(1)
def load_tokens_blacklist():
    logging.info("Started loading blacklist tokens")
    with open("/app/resources/tokens_blacklist.txt") as f:
        tokens_blacklist = {x.strip() for x in f.readlines()}
    logging.info("Successfully loaded blacklist tokens")
    return tokens_blacklist
