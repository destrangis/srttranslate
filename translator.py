
from subtitles import SubtitleFile, SubtitleRecord

def dummy_translate(from_lang, to_lang, txt):
    return f"({len(txt)} chars) {txt}"

class SrtTranslator:

    def __init__(self, filename="", translatefn=dummy_translate):
        self.translate = translatefn
        self.input = None
        self.input_language = ""
        self.output = {}
        if filename:
            self.add_input_filename(filename)
        self.chars = 0

    def add_input_filename(self, filename, language=""):
        self.input = SubtitleFile().read(filename)
        self.input_language = language

    def add_input_srt(self, sf, language=""):
        if not isinstance(sf, SubtitleFile):
            raise RuntimeError("SrtTranslator.add_input_srt() needs "
              f"argument of type SubtitleFile. Got {sf.__class__.__name__}")
        self.input = sf
        self.input_language = language

    def translate(self, to_lang="EN"):
        if not self.input:
            raise RuntimeError("SrtTranslator.translate() called with no input file")

        result = self.output[to_lang] = SubtitleFile()

        for sub in self.input:
            txt = "\n".join(sub.text)
            self.chars += len(txt)
            translated = self.translate(self.input_language, to_lang, txt)
            result.sublst.append(SubtitleRecord(sub.start, sub.end, translated.split("\n")))

    def write(self, to_lang, file):
        output = self.output.get(to_lang)
        if not output:
            raise RuntimeError(f'SrtTranslator.write() No output for language "{to_lang}"')
        output.write(file)