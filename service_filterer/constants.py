import re
import string


# Max number of characters to use for a title.
MAX_CHARS_TITLE = 300

# Minimum number of words in a title.
MIN_TITLE_WORD_CNT = 4

# Minimum number of known tokens in a title.
MIN_TITLE_TOKEN_CNT = 5

# Min threshold for news classification (using "Other" by default).
MIN_CLF_THRESHOLD = 0.25

# Min threshold for ignoring blacklisted tokens title presence.
BLACKLIST_OVERRIDE_THRESHOLD = 0.8

# Minimum number of characters in a word.
MIN_WORD_LEN = 2

# Regular expression for the title extraction.
TITLE_REGEX = re.compile('title.\s+content=.([^>]+)>')

# Regular expression for the description extraction.
DESC_REGEX = re.compile('description.\s+content=.([^>]+)>')

# Regular expression for the publication time extraction.
PUBLICATION_TIME_REGEX = re.compile('published_time.\s+content=.([^>]+)>')

# Regular expression for the URL extraction.
URL_REGEX = re.compile('url.\s+content=.([^>]+)>')

# Regular expression for "other" category.
OTHER_REGEX = re.compile(
    '(прогноз погоды|гороскоп|\sпогода|\sпогоду|тельцам|телец|\sовен|\sовнам|девам|стрелец|стрельцам|козерог|козерогу|козерогам|водолей|водолею|водолям|weather|horoscope|met eireann|lotto)\s')

# Regular expression for filtering out discounts.
# NOTE: not used, as apparently ads are allowed?
DISCOUNT_REGEX = re.compile('(\%|\d|percent)\soff\s')

# Regular expression for filtering out savings articles.
# NOTE: not used, as apparently ads are allowed?
SAVINGS_REGEX = re.compile('(save\s(£|\$|€|up))|(just\s(US)?(£|\$|€))|(for\s(£|\$|€))\d{2,3}(\.|$|\s)')

# Regular expression for filtering out sale-related articles.
SALE_REGEX = re.compile('(on|for) sale|(anniversary|apple|huge|amazon|friday|monday|christmas|fragrance|%) sale')

# Regular expression for banned phrases.
BAD_PHRASES_REGEX = re.compile(
    '(смотреть онлайн|можно приобрести|стоит всего|со скидкой|лучшие скидки|составлен топ|простой способ|простейший способ|способа|способов|free download|shouldn\'t miss|of the week|рецепт|правила|the week in)')

# Regular expression for filtering out articles with lists.
LIST_REGEX = re.compile(
    '\d+ (акци|банальн|важн|вещ|вопрос|главн|животн|знаменит|качествен|книг|лайфхак|лучш|мобил|необычн|популяр|привыч|прилож|причин|признак|продукт|прост|професс|самы|способ|технолог|худш|урок|шаг|факт|фильм|экзотичес|adorable|big|beaut|best|creative|crunchy|easy|huge|fantastic|innovative|iconic|baking|inspiring|perfect|stunning|stylish|unconventional|unexpected|wacky|wondeful|worst|habit|event|food|gift|question|reason|sign|step|thing|tip|trick|way)')
LIST_REGEX_STR_START = re.compile(
    '^\d+.{0,16} (акци|банальн|важн|вещ|вопрос|главн|животн|знаменит|качествен|книг|лайфхак|лучш|мобил|необычн|популяр|привыч|прилож|причин|признак|продукт|прост|професс|самы|способ|технолог|худш|урок|шаг|факт|фильм|экзотичес|adorable|big|beaut|best|creative|crunchy|easy|huge|fantastic|innovative|iconic|baking|inspiring|perfect|stunning|stylish|unconventional|unexpected|wacky|wondeful|worst|habit|event|food|gift|question|reason|sign|step|thing|tip|trick|way)')
LIST_REGEX_TOP = re.compile('^(the|top|топ)[\s-]\d+')

# Regular expression for filtering out "How to" guides and informational articles.
HOWTO_REGEX = re.compile(
    '^(best|check out|do you|got a|dont|get|have you|have YOU|here is|here are|how|let us|looking for|look for|my |say|should you|shall you|the best|the well|thi|this|these|useful tips|where|what|who|when|why|want|как|какие|какой|какую|почему|когда|куда|можно|стоит|почему|что\s|кто|с кем|кому|откуда|который|сколько|где|виды|лучшие|самы|зачем)\s')
HOWTO_ENDINGS_REGEX = r'как\s[а-я]+(ти|ть|сь|ся|чь)\b'

# Regular expression for filtering out titles based on their beginnings.
BAD_BEGINNINGS_REGEX = re.compile('^(commentary|review|removed|on this day):')

# Regular expression for repeated spaces.
SPACE_REP_REGEX = re.compile(r' +')

# Regular expression for digits.
DIGIT_REGEX = re.compile(r'\d')

# Regular expression for acronym detection.
ACRONYM_REGEX = re.compile(r'\b([A-ZА-Я]{2,4})\b')

# Punctuation replacement.
STR_TRANSLATE = str.maketrans(' ', ' ', string.punctuation.replace('$', ''))

# Stopwords for RU an EN.
STOPWORDS_RU = {'а', 'без', 'более', 'больше', 'будет', 'будто', 'бы', 'был', 'была', 'были', 'было', 'быть', 'в',
                'вам', 'вас', 'вдруг', 'ведь', 'во', 'вот', 'впрочем', 'все', 'всегда', 'всего', 'всех', 'всю', 'вы',
                'где', 'да', 'даже', 'два', 'для', 'до', 'другой', 'его', 'ее', 'ей', 'ему', 'если', 'есть', 'еще', 'ж',
                'же', 'за', 'зачем', 'здесь', 'и', 'из', 'или', 'им', 'иногда', 'их', 'к', 'как', 'какая', 'какой',
                'когда', 'конечно', 'кто', 'куда', 'ли', 'лучше', 'между', 'меня', 'мне', 'много', 'может', 'можно',
                'мой', 'моя', 'мы', 'на', 'над', 'надо', 'наконец', 'нас', 'не', 'него', 'нее', 'ней', 'нельзя', 'нет',
                'ни', 'нибудь', 'никогда', 'ним', 'них', 'ничего', 'но', 'ну', 'о', 'об', 'один', 'он', 'она', 'они',
                'опять', 'от', 'перед', 'по', 'под', 'после', 'потом', 'потому', 'почти', 'при', 'про', 'раз', 'разве',
                'с', 'сам', 'свою', 'себе', 'себя', 'сейчас', 'со', 'совсем', 'так', 'такой', 'там', 'тебя', 'тем',
                'теперь', 'то', 'тогда', 'того', 'тоже', 'только', 'том', 'тот', 'три', 'тут', 'ты', 'у', 'уж', 'уже',
                'хорошо', 'хоть', 'чего', 'чем', 'через', 'что', 'чтоб', 'чтобы', 'чуть', 'эти', 'этого', 'этой',
                'этом', 'этот', 'эту', 'я'}

# Title patterns for news filtering.
TITLE_PATTERNS_RU = {'W W: W W', 'W W W?', '№####', 'W W W!', '***', 'W W — W', 'W – W. ##.##.####. W W W W W', 'W!',
                     'W W!', 'W W W W!', '«W W W W»', '«W W W»', '«W W»', 'W W. W W', 'W–W', 'W-W', 'W W-W',
                     'W W - W W', 'W W – W W', 'W W...', 'W W W...', 'W W W W...', 'W W? W W W',
                     'W: W W ## W (W W ##.##.####)', 'W ## W. W W ##.##.####', 'W W W W. ## W', 'W – W. W W. W W',
                     'W W W ####', 'W W ##.##', 'W W (## W)', 'W: W W - ##', 'W W W? W W W W',
                     'W W: W W # W (W W ##.##.####)', 'W W: W W W (W W ##.##.####)'}
TITLE_PATTERNS_OTHER_RU = {'W W W ##.##.##', 'W W W W: W, ## W', 'W W W W: W, # W', 'W W ##.##.####',
                           'W W. W W ##.##.####', 'W W W W, ## W', 'W W ##.##.##', 'W W ## W #### W W W W',
                           'W W W ## W #### W.', '«W. W W» #.##.####', '«W. W W» ##.##.####',
                           '«W. W W» W ##. ##.##.####', '«W. W W» W ##. #.##.####', 'W W. W W ##.##.#### (##.##)',
                           'W W (W W ##.##.####)', 'W W W W # W (W)', 'W W W W W, ## W #### W', 'W W W ## W, W',
                           'W. W W ##.##.####', 'W W W W W ## W ####', 'W W ## W #### W', 'W W W W – ## W ####',
                           'W W ## W ####: W W W', 'W W W (## W)', 'W W W W W, ## W', 'W W W, ## W ####',
                           'W W W W W, # W', 'W W # W ####', '## W: W W, W W W W', 'W W W. W W ## W', '## W. W W',
                           '«W. W» ## W ####', 'W W. ## W', 'W W: # W ####', 'W W W W # W ####', 'W W # W #### W W W W'}
