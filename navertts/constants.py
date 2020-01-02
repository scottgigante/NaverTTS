import warnings

TRANSLATE_INIT = 'https://papago.naver.{tld}/apis/tts/makeID'
TRANSLATE_ENDPOINT = 'https://papago.naver.{tld}/apis/tts/{id}'
PREFIX = b'\xaeU\xae\xa1C\x9b,Uzd\xf8\xef'

LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
}

# https://apidocs.ncloud.com/en/ai-naver/clova_speech_synthesis/tts/
SPEAKERS = {
    'en' : {'f' : 'clara',
            'm' : 'matt'},
    'es' : {'f' : 'carmen',
            'm' : 'jose'},
    'ja' : {'m' : 'shinji'},
    'ko' : {'f' : 'mijin',
            'm' : 'jinho'},
    'zh' : {'f' : 'meimei',
            'm' : 'liangliang'},
}

def get_speaker(lang='ko', gender='f'):
    try:
        speakers = SPEAKERS[lang]
    except KeyError:
        raise ValueError("No speaker for language {}. "
                         "Available languages: {}".format(
                             lang, list(SPEAKERS.keys())))
    try:
        return speakers[gender]
    except KeyError:
        warnings.warn("Gender {} not available for language"
                      " {}".format(gender, lang))
        return list(speakers.values())[0]

def translate_init(tld='com'):
    return TRANSLATE_INIT.format(tld=tld)


def translate_endpoint(id, tld='com'):
    return TRANSLATE_ENDPOINT.format(id=id, tld=tld)
