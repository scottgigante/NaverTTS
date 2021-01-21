# -*- coding: utf-8 -*-
from .tokenizer import pre_processors, Tokenizer, tokenizer_cases
from .utils import _minimize, _len, _clean_tokens
from .lang import tts_langs
from . import constants

import urllib
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
import os

__all__ = ["NaverTTS", "NaverTTSError"]

# Logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Speed:
    """Read Speed."""

    SLOW = 5
    NORMAL = 0
    FAST = -5


class NaverTTS:
    """NaverTTS -- NAVER Text-to-Speech.

    An interface to NAVER Papago's Text-to-Speech API.

    Args:
        text (string): The text to be read.
        tld (string, optional): Top-level domain. Defaults to 'com'.
        lang (string, optional): The language (IETF language tag) to
            read the text in. Defaults to 'ko'.
        speed (str or int, optional): Choice of {'slow' (5), 'normal' (0), 'fast' (-5)}.
            Defaults to 'normal'.
        lang_check (bool, optional): Strictly enforce an existing ``lang``,
            to catch a language error early. If set to ``True``,
            a ``ValueError`` is raised if ``lang`` doesn't exist.
            Default is ``True``.
        pre_processor_funcs (list): A list of zero or more functions that are
            called to transform (pre-process) text before tokenizing. Those
            functions must take a string and return a string. Defaults to::

                [
                    pre_processors.tone_marks,
                    pre_processors.end_of_line,
                    pre_processors.abbreviations,
                    pre_processors.word_sub
                ]

        tokenizer_func (callable): A function that takes in a string and
            returns a list of string (tokens). Defaults to::

                Tokenizer([
                    tokenizer_cases.tone_marks,
                    tokenizer_cases.period_comma,
                    tokenizer_cases.colon,
                    tokenizer_cases.other_punctuation
                ]).run

    See Also:
        :doc:`Pre-processing and tokenizing <tokenizer>`

    Raises:
        AssertionError: When ``text`` is ``None`` or empty; when there's nothing
            left to speak after pre-precessing, tokenizing and cleaning.
        ValueError: When ``lang_check`` is ``True`` and ``lang`` is not supported.
        RuntimeError: When ``lang_check`` is ``True`` but there's an error loading
            the languages dictionnary.

    """

    NAVER_TTS_MAX_CHARS = 100  # Max characters the NAVER TTS API takes at a time
    NAVER_TTS_HEADERS = {
        "Referer": "http://papago.naver.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/47.0.2526.106 Safari/537.36",
    }

    def __init__(
        self,
        text,
        lang="ko",
        tld="com",
        speed="normal",
        gender="f",
        lang_check=True,
        pre_processor_funcs=[
            pre_processors.tone_marks,
            pre_processors.end_of_line_hyphen,
            pre_processors.newline,
            pre_processors.abbreviations,
            pre_processors.word_sub,
        ],
        tokenizer_func=Tokenizer(
            [
                tokenizer_cases.tone_marks,
                tokenizer_cases.period_comma,
                tokenizer_cases.colon,
                tokenizer_cases.other_punctuation,
            ]
        ).run,
    ):

        # Debug
        for k, v in locals().items():
            if k == "self":
                continue
            log.debug("%s: %s", k, v)

        # Text
        assert text, "No text to speak"
        self.text = text

        # Translate URL top-level domain
        self.tld = tld

        # Language
        if lang_check:
            try:
                langs = tts_langs(self.tld)
                if lang.lower() not in langs:
                    raise ValueError("Language not supported: %s" % lang)
            except RuntimeError as e:
                log.debug(str(e), exc_info=True)
                log.warning(str(e))

        self.lang_check = lang_check
        self.lang = lang.lower()
        self.speaker = constants.get_speaker(self.lang, gender)

        # Read speed
        if speed == "slow":
            self.speed = Speed.SLOW
        elif speed == "normal":
            self.speed = Speed.NORMAL
        elif speed == "fast":
            self.speed = Speed.FAST
        elif isinstance(speed, int) and -5 <= speed and speed <= 5:
            self.speed = speed
        else:
            raise ValueError(
                "Expected `speed` in 'slow', 'normal', "
                "'fast' or an integer between -5 and 5."
                " Got {}".format(speed)
            )

        # Pre-processors and tokenizer
        self.pre_processor_funcs = pre_processor_funcs
        self.tokenizer_func = tokenizer_func

    def _tokenize(self, text):
        # Pre-clean
        text = text.strip()

        # Apply pre-processors
        for pp in self.pre_processor_funcs:
            log.debug("pre-processing: %s", pp)
            text = pp(text)

        if _len(text) <= self.NAVER_TTS_MAX_CHARS:
            return _clean_tokens([text])

        # Tokenize
        log.debug("tokenizing: %s", self.tokenizer_func)
        tokens = self.tokenizer_func(text)

        # Clean
        tokens = _clean_tokens(tokens)

        # Minimize
        min_tokens = []
        for t in tokens:
            min_tokens += _minimize(t, " ", self.NAVER_TTS_MAX_CHARS)
        return min_tokens

    def write_to_fp(self, fp):
        """Do the TTS API request and write bytes to a file-like object.

        Args:
            fp (file object): Any file-like object to write the ``mp3`` to.

        Raises:
            :class:`gTTSError`: When there's an error with the API request.
            TypeError: When ``fp`` is not a file-like object that takes bytes.

        """
        # When disabling ssl verify in requests (for proxies and firewalls),
        # urllib3 prints an insecure warning on stdout. We disable that.
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        text_parts = self._tokenize(self.text)
        log.debug("text_parts: %i", len(text_parts))
        assert text_parts, "No text to send to TTS API"

        for idx, part in enumerate(text_parts):

            endpoint_url = constants.translate_endpoint(
                text=part, speaker=self.speaker, speed=self.speed, tld=self.tld
            )
            try:
                # Request
                r = requests.get(
                    url=endpoint_url,
                    headers=self.NAVER_TTS_HEADERS,
                    proxies=urllib.request.getproxies(),
                    verify=False,
                )

                log.debug("headers-%i: %s", idx, r.request.headers)
                log.debug("url-%i: %s", idx, r.request.url)
                log.debug("status-%i: %s", idx, r.status_code)

                r.raise_for_status()
            except requests.exceptions.HTTPError as e:  # pragma: no cover
                # Request successful, bad response
                log.debug(str(e))
                raise NaverTTSError(tts=self, response=r)
            except requests.exceptions.RequestException as e:  # pragma: no cover
                # Request failed
                log.debug(str(e))
                raise NaverTTSError(tts=self)

            try:
                for chunk in r.iter_content(chunk_size=1024):
                    fp.write(chunk)
                log.debug("part-%i written to %s", idx, fp)
            except (AttributeError, TypeError) as e:
                raise TypeError(
                    "'fp' is not a file-like object or it does not take bytes: %s"
                    % str(e)
                )

    def save(self, savefile):
        """Do the TTS API request and write result to file.

        Args:
            savefile (string): The path and file name to save the ``mp3`` to.

        Raises:
            :class:`NaverTTSError`: When there's an error with the API request.

        """
        savefile = str(savefile)
        try:
            with open(savefile, "wb") as f:
                self.write_to_fp(f)
                log.debug("Saved to %s", savefile)
        except NaverTTSError:
            os.remove(savefile)
            raise


class NaverTTSError(Exception):
    """Exception that uses context to present a meaningful error message."""

    def __init__(self, msg=None, **kwargs):
        self.tts = kwargs.pop("tts", None)
        self.rsp = kwargs.pop("response", None)
        if msg:
            self.msg = msg
        elif self.tts is not None:
            self.msg = self.infer_msg(self.tts, self.rsp)
        else:
            self.msg = None
        super(NaverTTSError, self).__init__(self.msg)

    def infer_msg(self, tts, rsp=None):
        """Attempt to guess what went wrong.

        Uses known information (e.g. http response) and observed behaviour.

        """
        cause = "Unknown"

        if rsp is None:
            premise = "Failed to connect"

            if tts.tld != "com":
                host = constants.translate_base(tld=tts.tld)
                cause = "Host '{}' is not reachable".format(host)

        else:
            # rsp should be <requests.Response>
            # http://docs.python-requests.org/en/master/api/
            status = rsp.status_code
            reason = rsp.reason

            premise = "{:d} ({}) from TTS API".format(status, reason)

            if status == 403:
                cause = "Bad token or upstream API changes"
            elif status == 404 and not tts.lang_check:
                cause = "Unsupported language '%s'" % self.tts.lang
            elif status >= 500:
                cause = "Uptream API error. Try again later."

        return "{}. Probable cause: {}".format(premise, cause)
