# -*- coding: utf-8 -*-
from . import __version__
from . import NaverTTS
from . import NaverTTSError
from .lang import tts_langs
import click
import logging
import logging.config

# Click settings
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

# Logger settings
LOGGER_SETTINGS = {
    "version": 1,
    "formatters": {"default": {"format": "%(name)s - %(levelname)s - %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "loggers": {"navertts": {"handlers": ["console"], "level": "WARNING"}},
}

# Logger
logging.config.dictConfig(LOGGER_SETTINGS)
log = logging.getLogger("navertts")


def sys_encoding():
    """Charset to use for --file <path>|- (stdin)."""
    return "utf8"


def validate_text(ctx, param, text):
    """Validate <text> argument.

    Ensures <text> (arg) and <file> (opt) are mutually exclusive
    """
    if not text and "file" not in ctx.params:
        # No <text> and no <file>
        return "-"
    elif text and "file" in ctx.params:
        # Both <text> and <file>
        raise click.BadParameter("<text> and -f/--file <file> can't be used together")
    elif text and isinstance(text, tuple):
        return " ".join(text)
    else:
        return text


def validate_lang(ctx, param, lang):
    """Validate <lang> option.

    Ensures <lang> is a supported language unless the <nocheck> flag is set
    Uses <tld> to fetch languages from other domains
    """
    if ctx.params["nocheck"]:
        return lang

    try:
        tld = ctx.params["tld"]
        if lang not in tts_langs(tld):
            raise click.UsageError(
                "'%s' not in list of supported languages.\n"
                "Use --all to list languages or "
                "add --nocheck to disable language check." % lang
            )
        else:
            # The language is valid.
            # No need to let NaverTTS re-validate.
            ctx.params["nocheck"] = True
    except RuntimeError as e:
        # Only case where the <nocheck> flag can be False
        # Non-fatal. gTTS will try to re-validate.
        log.debug(str(e), exc_info=True)

    return lang


def validate_speed(ctx, param, speed):
    """Validate <speed> option.

    Ensures <speed> is a supported language unless the <nocheck> flag is set
    Uses <tld> to fetch languages from other domains
    """
    if speed in ["slow", "normal", "fast"]:
        return speed

    try:
        return int(speed)
    except TypeError:
        raise click.UsageError(
            "'%s' not in list of supported speeds.\n"
            "Choose from ['slow', 'normal', 'fast'] or "
            "an integer between -5 (fast) and 5 (slow)." % speed
        )


def print_languages(ctx, param, value):
    """Print all languages.

    Prints formatted sorted list of supported languages and exits
    """
    if not value or ctx.resilient_parsing:
        return

    try:
        tld = ctx.params["tld"]
    except KeyError:
        # Either --tld was used after --all or not at all
        # Default to the 'com' tld
        tld = "com"

    try:
        langs = tts_langs(tld)
        langs_str_list = sorted("{}: {}".format(k, langs[k]) for k in langs)
        click.echo("  " + "\n  ".join(langs_str_list))
    except RuntimeError as e:  # pragma: no cover
        log.debug(str(e), exc_info=True)
        raise click.ClickException("Couldn't fetch language list.")
    ctx.exit()


def set_debug(ctx, param, debug):
    """Set logger level to DEBUG."""
    if debug:
        log.setLevel(logging.DEBUG)
    return


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "text", metavar="<text>", nargs=-1, required=False, callback=validate_text
)
@click.option(
    "-f",
    "--file",
    metavar="<file>",
    # For py2.7/unicode. If encoding not None Click uses io.open
    type=click.File(encoding=sys_encoding()),
    help="Read from <file> instead of <text>.",
)
@click.option(
    "-o",
    "--output",
    metavar="<file>",
    type=click.File(mode="wb"),
    help="Write to <file> instead of stdout.",
)
@click.option(
    "-s",
    "--speed",
    metavar="<speed>",
    default="normal",
    show_default=True,
    callback=validate_speed,
    help="Reading speed. Choose from 'slow', 'normal', 'fast' "
    "or an integer between -5 (fast) and 5 (slow).",
)
@click.option(
    "-l",
    "--lang",
    metavar="<lang>",
    default="ko",
    show_default=True,
    callback=validate_lang,
    help="IETF language tag. Language to speak in. List documented tags with --all.",
)
@click.option(
    "-t",
    "--tld",
    metavar="<tld>",
    default="com",
    show_default=True,
    is_eager=True,  # Prioritize <tld> to ensure it gets set before <lang>
    help="Top-level domain for the Google host, i.e https://translate.google.<tld>",
)
@click.option(
    "--nocheck",
    default=False,
    is_flag=True,
    is_eager=True,  # Prioritize <nocheck> to ensure it gets set before <lang>
    help="Disable strict IETF language tag checking. Allow undocumented tags.",
)
@click.option(
    "--all",
    default=False,
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=print_languages,
    help="Print all documented available IETF language tags and exit. "
    "Use --tld beforehand to use an alternate domain",
)
@click.option(
    "--debug",
    default=False,
    is_flag=True,
    is_eager=True,  # Prioritize <debug> to see debug logs of callbacks
    expose_value=False,
    callback=set_debug,
    help="Show debug information.",
)
@click.version_option(version=__version__)
def tts_cli(text, file, output, speed, tld, lang, nocheck):
    """Read <text> to mp3 format using NAVER Papago's Text-to-Speech API.

    (set <text> or --file <file> to - for standard input)
    """
    # stdin for <text>
    if text == "-":
        text = click.get_text_stream("stdin").read()

    # stdout (when no <output>)
    if not output:
        output = click.get_binary_stream("stdout")

    # <file> input (stdin on '-' is handled by click.File)
    if file:
        try:
            text = file.read()
        except UnicodeDecodeError as e:  # pragma: no cover
            log.debug(str(e), exc_info=True)
            raise click.FileError(
                file.name, "<file> must be encoded using '%s'." % sys_encoding()
            )

    # TTS
    try:
        tts = NaverTTS(
            text=text, lang=lang, speed=speed, tld=tld, lang_check=not nocheck
        )
        tts.write_to_fp(output)
    except (ValueError, AssertionError) as e:
        raise click.UsageError(str(e))
    except NaverTTSError as e:
        raise click.ClickException(str(e))
