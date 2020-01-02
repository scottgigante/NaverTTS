# NaverTTS

<img width=600 src="https://raw.githubusercontent.com/scottgigante/NaverTTS/master/papago.svg?sanitize=true">

**NaverTTS** (*NAVER Text-to-Speech*), a Python library and CLI tool to interface with NAVER Papago's text-to-speech API. 
Writes spoken `mp3` data to a file, a file-like object (bytestring) for further audio
manipulation, or `stdout`.

[![PyPI version](https://img.shields.io/pypi/v/NaverTTS.svg)](https://pypi.org/project/NaverTTS/)
[![Python versions](https://img.shields.io/pypi/pyversions/NaverTTS.svg)](https://pypi.org/project/NaverTTS/)
[![PyPi Downloads](http://pepy.tech/badge/NaverTTS)](http://pepy.tech/project/NaverTTS)
[![Travis CI Build](https://api.travis-ci.com/scottgigante/NaverTTS.svg?branch=master)](https://travis-ci.com/scottgigante/NaverTTS)

## Features

-   Customizable speech-specific sentence tokenizer that allows for unlimited lengths of text to be read, all while keeping proper intonation, abbreviations, decimals and more;
-   Customizable text pre-processors which can, for example, provide pronunciation corrections;
-   Automatic retrieval of supported languages.

### Installation

    $ pip install NaverTTS

### Quickstart

Command Line:

    $ navertts-cli --output hello.mp3 hello

Module:

    >>> from navertts import NaverTTS
    >>> tts = NaverTTS('hello')
    >>> tts.save('hello.mp3')

### Licence

This project was adapted from [gTTS](https://github.com/pndurette/gTTS) under the [The MIT License (MIT)](LICENSE). gTTS Copyright © 2014-2019 Pierre Nicolas Durette. NaverTTS Copyright © 2019 Scott Gigante.
