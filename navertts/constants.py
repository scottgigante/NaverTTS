import warnings

TRANSLATE_ENDPOINT = "https://dict.naver.{tld}/api/nvoice"
TRANSLATE_PARAMS = (
    "?service=dictionary&speech_fmt=mp3&text={text}&speaker={speaker}&speed={speed}"
)

LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}

# https://apidocs.ncloud.com/en/ai-naver/clova_speech_synthesis/tts/
SPEAKERS = {
    "en": {"f": "clara", "m": "matt"},
    "es": {"f": "carmen", "m": "jose"},
    "ja": {"f": "nsayuri", "m": "shinji"},
    "ko": {"f": "kyuri", "m": "jinho"},
    "zh": {"f": "meimei", "m": "liangliang"},
}


def get_speaker(lang="ko", gender="f"):
    """Get the API name for the chosen speaker."""
    try:
        speakers = SPEAKERS[lang]
    except KeyError:
        raise ValueError(
            "No speaker for language {}. "
            "Available languages: {}".format(lang, list(SPEAKERS.keys()))
        )
    try:
        return speakers[gender]
    except KeyError:
        warnings.warn("Gender {} not available for language" " {}".format(gender, lang))
        return list(speakers.values())[0]


def translate_base(tld="com"):
    """Get the base URL."""
    return TRANSLATE_ENDPOINT.format(tld=tld)


def translate_endpoint(text, speaker="kyuri", speed=0, tld="com"):
    """Get the endpoint URL."""
    url = translate_base(tld=tld)
    return url + TRANSLATE_PARAMS.format(text=text, speaker=speaker, speed=speed)
