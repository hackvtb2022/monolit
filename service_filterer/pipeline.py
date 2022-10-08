import re

from service_filterer import constants
from service_filterer.models import PipelineRequest, PipelineResponse
from service_filterer.utils import clean_string, filter_news, get_title_pattern


class Pipeline:
    def __init__(self):
        ...

    def run(self, request: PipelineRequest) -> PipelineResponse:
        original_title = request.title
        original_title = original_title.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'")
        title_with_digits = clean_string(request.title[:constants.MAX_CHARS_TITLE])
        title = re.sub(constants.DIGIT_REGEX, '', title_with_digits)
        is_valid = filter_news({
            "title": title,
            "original_title": original_title,
            "title_with_digits": title_with_digits,
            "category_confidence": 1.0,
            "language": "ru",
            "title_pattern": get_title_pattern(original_title)
        })
        return PipelineResponse(is_valid=is_valid)
