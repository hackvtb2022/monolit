import logging
import functools

from fastapi import FastAPI, Depends
from service_filterer.pipeline import Pipeline
from service_filterer.models import PipelineRequest, PipelineResponse


app = FastAPI()


@functools.lru_cache(1)
def load_pipeline() -> Pipeline:
    logging.info("Started loading pipeline")
    pipeline = Pipeline()
    logging.info("Successfully loaded pipeline")
    return pipeline


@app.post("/filterer")
def read_root(request: PipelineRequest, pipeline: Pipeline = Depends(load_pipeline)) -> PipelineResponse:
    response = pipeline.run(request)
    return response
