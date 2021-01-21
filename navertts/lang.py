# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import logging
import re
from . import constants

__all__ = ["tts_langs"]

# Logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def tts_langs(tld="com"):
    """Languages Naver Text-to-Speech supports.

    Args:
        tld (string): Top-level domain for the Google Translate host
            to fetch languages from. i.e `https://translate.google.<tld>`.
            Default is ``com``.

    Returns:
        dict: A dictionnary of the type `{ '<lang>': '<name>'}`

        Where `<lang>` is an IETF language tag such as `en` or `pt-br`,
        and `<name>` is the full English name of the language, such as
        `English` or `Portuguese (Brazil)`.

    The dictionnary returned combines languages from two origins:

    - Languages fetched automatically from Google Translate
    - Languages that are undocumented variations that were observed to work and
      present different dialects or accents.

    """
    try:
        langs = dict()
        # log.debug("Fetching with '{}' tld".format(tld))
        # langs.update(_fetch_langs(tld))
        langs.update(_extra_langs())
        log.debug("langs: {}".format(langs))
        return langs
    except Exception as e:
        raise RuntimeError("Unable to get language list: {}".format(str(e)))


def _extra_langs():
    """Define extra languages.

    Returns:
        dict: A dictionnary of extra languages manually defined.
    """
    return constants.LANGUAGES
