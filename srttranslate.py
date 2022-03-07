import os
import sys
import pathlib
import argparse

from translator import SrtTranslator, OutOfQuotaError, TranslatorError
from deeplhandler import DeeplHandler


def translate_subtitles(subfile, outfile, api_key):
    print(f"Translating {subfile} into {outfile} using key {api_key}")
    #return 0
    breakpoint()
    handler = DeeplHandler(api_key)
    transl = SrtTranslator(handler).add_input_file(subfile)
    transl.translate("EN-GB")
    transl.write("EN-GB", outfile)


def get_api_key(cliopts):
    if cliopts.keyfile:
        with cliopts.keyfile.open() as kfd:
            return kfd.read().strip()

    return os.getenv("DEEPL_API_KEY", "")


def get_command_line_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyfile", "-k", metavar="KEYFILE",
            type=pathlib.Path,
            help="Name of file containing DeepL's API key")
    parser.add_argument("--output", "-o", metavar="FILE",
            type=pathlib.Path,
            help="Name of output subtitle file")
    parser.add_argument("SUBFILE",
            type=pathlib.Path,
            help="Subtitle file to translate")
    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    cliopts = get_command_line_args(argv)

    api_key = get_api_key(cliopts)
    if not api_key:
        print("No API key for DeepL", file=sys.stderr)
        print("Please provide a file that contains the API Key or set "
              "the DEEPL_API_KEY environment variable to the key",
              file=sys.stderr)
        return 1

    if cliopts.output:
        output = cliopts.output
    else:
        output = cliopts.SUBFILE.parent / (cliopts.SUBFILE.stem + ".en.srt")

    translate_subtitles(cliopts.SUBFILE, output, api_key)

    return 0


if __name__ == "__main__":
    sys.exit(main())
