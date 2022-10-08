import re

from service_filterer import constants
from service_filterer.factory import load_word2norm, load_tokens, load_tokens_blacklist


tokens = load_tokens()
word2norm = load_word2norm()
tokens_blacklist = load_tokens_blacklist()


def lowercase_except_acronyms(input_str):
    """Convert a string to a lower case (except acronyms)."""
    result_str = input_str.lower()

    # No way of knowing if anything is an acronym.
    if input_str.isupper():
        return result_str

    for m in constants.ACRONYM_REGEX.finditer(input_str):
        start = m.start()
        end = m.start() + len(m.group())
        result_str = result_str[:start] + result_str[start:end].upper() + result_str[end:]
    return result_str


def clean_string(input_str):
    """Prepare an input string for TF-IDF and classification."""
    input_str = lowercase_except_acronyms(input_str.strip()).replace('&quot;', '').replace(
        '\xa0', ' ').replace('\xad', '').replace('«', '').replace('»', '').replace(
        '‘', '').replace('’', ' ').replace('-', ' ').replace('–', ' ').replace('£', ' £ ').replace(
        '₹', ' ₹ ').replace('€', ' € ').replace('$', ' $ ').replace(',', '').replace(
        '.', '').translate(constants.STR_TRANSLATE)

    input_str = re.sub(constants.SPACE_REP_REGEX, ' ', input_str)
    input_str = ' '.join([word2norm.get(x, x) for x in input_str.split(' ')])
    return input_str


def replace_digits(input_str):
    """Replace digits for title pattern generation."""
    return '#' * len(input_str.group())


def get_title_pattern(input_str):
    """Get a title punctuation pattern."""
    return re.sub(r'\w+', 'W', re.sub(r'\d+', replace_digits, input_str))


def filter_news(a):
    """Filter out non-news articles."""
    title_lower = a['original_title'].lower()
    title_words = a['title_with_digits'].split(' ')
    title_words_set = set(x for x in title_words if len(x) >= constants.MIN_WORD_LEN or re.search(r'в|о|с|у|\d', x))

    # Allow articles which have whitelisted tokens or get confidently classified.
    is_whitelisted = (len(tokens & title_words_set) > 0
                      or (a['category_confidence'] >= constants.MIN_CLF_THRESHOLD))

    # Ignore articles which contain blacklisted tokens (ignore high-confidence cases).
    is_not_blacklisted = ((len(tokens_blacklist & title_words_set) == 0)
                          or a['category_confidence'] > constants.BLACKLIST_OVERRIDE_THRESHOLD)

    # # Ignore discount and savings titles.
    is_not_discount = not (re.search(constants.DISCOUNT_REGEX, a['title']) or re.search(constants.SAVINGS_REGEX, title_lower))

    # # Ignore sale titles.
    is_not_sale = not re.search(constants.SALE_REGEX, a['title'])

    # Ignore "How to" articles.
    is_not_howto = not re.search(constants.HOWTO_REGEX, a['title_with_digits'])
    is_not_howto = is_not_howto and not (
                re.search(constants.HOWTO_ENDINGS_REGEX, a['original_title']) and len(tokens & title_words_set) == 0)

    # Ignore articles with bad phrases in titles.
    is_not_bad_phrase = not re.search(constants.BAD_PHRASES_REGEX, a['title'])

    # Ignore articles based on how their titles begin.
    is_not_bad_beginnings = not re.search(constants.BAD_BEGINNINGS_REGEX, a['original_title'])

    # Ignore articles with lists (such as "10 tips for...").
    is_not_list = not re.search(constants.LIST_REGEX, title_lower)
    is_not_list_str_start = not re.search(constants.LIST_REGEX_STR_START, title_lower)
    is_not_list_top = not re.search(constants.LIST_REGEX_TOP, title_lower)

    # Ignore abnormally short titles.
    is_not_low_word_cnt = len(title_words_set) >= constants.MIN_TITLE_WORD_CNT

    # Ignore mid-short titles with no whitelisted terms.
    is_not_mid_low_word_cnt = not (len(title_words_set) == 4 and len(tokens & title_words_set) == 0)

    # Ignore low-confidence questions.
    is_not_low_quality_question = not (
                title_lower and (title_lower[-1] == '?') and (a['category_confidence'] < 0.75))

    # Ignore "Artist - ItemName" titles.
    is_not_dash = not (
                '—' in a['original_title'] and len(tokens & title_words_set) == 0 and len(title_words) <= 5)

    # Ignore titles with a slash.
    is_not_slash = not (' / ' in a['original_title'])

    # Ignore exclamations.
    is_not_exclamation = not (a['original_title'][-1] == '!' and len(title_words_set) < 8)

    # Ignore ellipses.
    is_not_ellipsis = not (
                a['original_title'][-3:] == '...' and a['category_confidence'] < 0.8 and len(title_words_set) < 7)

    # Ignore full quotes.
    is_not_quote = not (
                a['original_title'][0] == '«' and a['original_title'][-1] == '»' and a['original_title'].count(
            '«') == 1 and a['original_title'].count('»') == 1)

    # Ignore patterns which follow a certain template.
    is_not_templated_pattern = not (a['title_pattern'] in constants.TITLE_PATTERNS_RU)

    if (is_whitelisted and is_not_blacklisted and is_not_howto and is_not_bad_phrase
            and is_not_bad_beginnings and is_not_list and is_not_list_str_start and is_not_list_top
            and is_not_low_word_cnt and is_not_mid_low_word_cnt
            and is_not_low_quality_question and is_not_dash and is_not_slash
            and is_not_exclamation and is_not_ellipsis and is_not_quote and is_not_templated_pattern
            and is_not_discount and is_not_sale):
        return True
    return False
