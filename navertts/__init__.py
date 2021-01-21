# -*- coding: utf-8 -*-
from .version import __version__  # noqa: F401
from .tts import NaverTTS, NaverTTSError

__all__ = ["NaverTTS", "NaverTTSError"]
