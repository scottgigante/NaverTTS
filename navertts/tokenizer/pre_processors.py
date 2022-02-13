# -*- coding: utf-8 -*-
from . import PreProcessorRegex
from . import PreProcessorSub
from . import symbols
import re


def tone_marks(text):
    """Add a space after tone-modifying punctuation.

    Because the `tone_marks` tokenizer case will split after a tone-modidfying
    punctuation mark, make sure there's whitespace after.

    """
    return PreProcessorRegex(
        search_args=symbols.TONE_MARKS,
        search_func=lambda x: "(?<={})".format(x),
        repl=" ",
    ).run(text)


def end_of_line_hyphen(text):
    """Re-form words cut by end-of-line hyphens.

    Remove "<hyphen><newline>".

    """
    return PreProcessorRegex(
        search_args="-", search_func=lambda x: "{}\n".format(x), repl=""
    ).run(text)


def newline(text):
    """Replace <newline> with <space>."""
    return PreProcessorRegex(
        search_args="\n", search_func=lambda x: "{}".format(x), repl=" "
    ).run(text)


def abbreviations(text):
    """Fix tokenization of abbreviations.

    Removes periods after an abbreviation from a list of known
    abbrevations that can be spoken the same without that period. This
    prevents having to handle tokenization of that period.

    Note:
        Could potentially remove the ending period of a sentence.

    Note:
        Abbreviations that Google Translate can't pronounce without
        (or even with) a period should be added as a word substitution with a
        :class:`PreProcessorSub` pre-processor. Ex.: 'Esq.', 'Esquire'.

    """
    return PreProcessorRegex(
        search_args=symbols.ABBREVIATIONS,
        search_func=lambda x: r"(?<={})(?=\.).".format(x),
        repl="",
        flags=re.IGNORECASE,
    ).run(text)


def word_sub(text):
    """Word-for-word substitutions."""
    return PreProcessorSub(sub_pairs=symbols.SUB_PAIRS).run(text)
