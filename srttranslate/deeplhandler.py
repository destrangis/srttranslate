import deepl

# with open("deepl.key") as fd:
# deepl_api_key = fd.read().strip()


class DeeplHandler:
    def __init__(self, deepl_api_key):
        self.transl = deepl.Translator(deepl_api_key)
        usage = self.transl.get_usage()
        self.chars = usage.character.count
        self.limit = usage.character.limit

    def translate(self, inlang, outlang, txt):
        if inlang == "EN-GB":
            inlang = "EN"
        if outlang == "EN":
            outlang = "EN-GB"

        try:
            rsp = self.transl.translate_text(
                txt, source_lang=inlang, target_lang=outlang
            )
        except Exception:
            raise
        else:
            self.chars += len(txt)
        return rsp.text

    def check_quota(self, nchars):
        # True-- we can translate nchars False-- we can't
        return (self.chars + nchars) <= self.limit
