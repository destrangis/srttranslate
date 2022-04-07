from .subtitles import SubtitleFile, SubtitleRecord


class TranslatorError(Exception):
    pass


class OutOfQuotaError(TranslatorError):
    pass


class SrtTranslator:
    def __init__(self, handler, filename="", progressfn=lambda x, y: None):
        self.input = None
        self.input_language = ""
        self.output = {}
        self.handler = handler
        self.progressfn = progressfn
        if filename:
            self.add_input_file(filename)
        self.chars = 0

    def add_input_file(self, file, language=""):
        self.input = SubtitleFile().read(file).remove_empty_subtitles()
        self.input_language = language
        return self

    def add_input_srt(self, sf, language=""):
        if not isinstance(sf, SubtitleFile):
            raise TranslatorError(
                "SrtTranslator.add_input_srt() needs "
                f"argument of type SubtitleFile. Got {sf.__class__.__name__}"
            )
        self.input = sf
        self.input_language = language
        return self

    def translate(self, to_lang="EN-GB"):
        if not self.input:
            raise TranslatorError("SrtTranslator.translate() called with no input file")

        chars_needed = self.input.count_content_chars()
        if not self.handler.check_quota(chars_needed):
            raise OutOfQuotaError(
                "No quota."
                f"\n\tNeeded: {chars_needed}"
                f"\n\tAvaliable: {self.handler.limit - self.handler.chars}"
            )

        result = self.output[to_lang] = SubtitleFile()

        for i, sub in enumerate(self.input):
            txt = "\n".join(sub.text)
            self.chars += len(txt)
            self.progressfn(chars_needed, self.chars)
            translated = self.handler.translate(self.input_language, to_lang, txt)
            result.sublst.append(
                SubtitleRecord(sub.start, sub.end, translated.split("\n"))
            )

        return self

    def write(self, to_lang, file):
        output = self.output.get(to_lang)
        if not output:
            raise TranslatorError(
                f'SrtTranslator.write() No output for language "{to_lang}"'
            )
        output.write(file)
        return self
