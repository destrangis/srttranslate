import os
import sys
import pathlib
import argparse
import importlib.resources

from .translator import SrtTranslator
from .deeplhandler import DeeplHandler


def progress_report(maxchars, chars_to_now):
    percent = chars_to_now * 100 / maxchars
    print(f"\r{percent:5.1f}%", end="")


def translate_subtitles(subfile, outfile, api_key):
    print(f"Translating {subfile} into {outfile}")
    handler = DeeplHandler(api_key)
    print(f"{handler.chars} used of {handler.limit} available.")
    transl = SrtTranslator(handler, progressfn=progress_report)
    transl.add_input_file(subfile)
    transl.translate("EN-GB")
    print(f"\nWriting {outfile}")
    transl.write("EN-GB", outfile)
    print(
        f"Done. {transl.chars} Characters translated. "
        f"Total {handler.chars+transl.chars} so far."
    )


def get_api_key(cliopts):
    if cliopts.keyfile:
        with cliopts.keyfile.open() as kfd:
            return kfd.read().strip()

    return os.getenv("DEEPL_API_KEY", "")


def get_command_line_args(version, argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + version,
        help="print version and exit",
    )
    parser.add_argument(
        "--keyfile",
        "-k",
        metavar="KEYFILE",
        type=pathlib.Path,
        help="name of file containing DeepL's API key",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        type=pathlib.Path,
        help="name of output subtitle file",
    )
    parser.add_argument("SUBFILE", type=pathlib.Path, help="Subtitle file to translate")
    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    pkgname = __name__.split(".")[0]
    with importlib.resources.open_text(pkgname, "VERSION") as vfd:
        version = vfd.read().strip()

    cliopts = get_command_line_args(version, argv)

    api_key = get_api_key(cliopts)
    if not api_key:
        print("No API key for DeepL", file=sys.stderr)
        print(
            "Please provide a file that contains the API Key or set "
            "the DEEPL_API_KEY environment variable to the key",
            file=sys.stderr,
        )
        return 1

    if cliopts.output:
        output = cliopts.output
    else:
        output = cliopts.SUBFILE.parent / (cliopts.SUBFILE.stem + ".en.srt")

    translate_subtitles(cliopts.SUBFILE, output, api_key)

    return 0


if __name__ == "__main__":
    sys.exit(main())
