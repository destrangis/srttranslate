import codecs
import unittest
from io import StringIO
from textwrap import dedent

from srttranslate.translator import SrtTranslator, TranslatorError, OutOfQuotaError
from srttranslate.subtitles import SubtitleFile


class DummyHandler:
    # Handlers need:
    #  - a translate() method
    #  - a check_quota(x) method, True if nchars is in quota, False if not
    #  - chars attribute - chars consumed in the period
    #  - limit attribute - max chars allowed in the period
    #
    # This one is for testing. Translation is rot13 and quota, chars and
    # limits are user settable
    def __init__(self, in_quota=True, chars=0, limit=100_000_000):
        self.in_quota = in_quota
        self.chars = chars
        self.limit = limit

    def translate(self, from_lang, to_lang, txt):
        return codecs.encode(txt, "rot13")

    def check_quota(self, nchars):
        return self.in_quota


class TestTranslator(unittest.TestCase):
    def test_translator_translates_from_file(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             Start of a movie

             2
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!

             3
             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        expected = [
            "00:00:00,500 --> 00:00:03,000\nFgneg bs n zbivr\n",
            "00:01:12,629 --> 00:01:15,183\n"
            "- Uryyb, Zf. Jvyxvaf!\n"
            "- Tbbq zbeavat!\n",
            "00:01:17,321 --> 00:01:19,742\n" "Ab, hfr gur bgure qbbe, cyrnfr\n",
        ]

        handler = DummyHandler()
        trans = SrtTranslator(handler).add_input_file(subfile, "EN-GB")
        trans.translate("ROT13")

        self.assertEqual(3, len(list(trans.output["ROT13"])))
        for xsub, expstr in zip(trans.output["ROT13"], expected):
            self.assertEqual(str(xsub), expstr)

    def test_translator_translates_from_srt_object(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             Start of a movie

             2
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!

             3
             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        expected = [
            "00:00:00,500 --> 00:00:03,000\nFgneg bs n zbivr\n",
            "00:01:12,629 --> 00:01:15,183\n"
            "- Uryyb, Zf. Jvyxvaf!\n"
            "- Tbbq zbeavat!\n",
            "00:01:17,321 --> 00:01:19,742\n" "Ab, hfr gur bgure qbbe, cyrnfr\n",
        ]

        sf = SubtitleFile().read(subfile)
        handler = DummyHandler()
        trans = SrtTranslator(handler).add_input_srt(sf, "EN-GB")
        trans.translate("ROT13")

        self.assertEqual(3, len(list(trans.output["ROT13"])))
        for xsub, expstr in zip(trans.output["ROT13"], expected):
            self.assertEqual(str(xsub), expstr)

    def test_bad_srt_object_raises_exception(self):
        class DummyObject:  # NOT a SubtitleFile object
            pass

        trans = SrtTranslator(DummyHandler())
        with self.assertRaises(TranslatorError):
            trans.add_input_srt(DummyObject())

    def test_bad_output_lang_raises_exception(self):
        trans = SrtTranslator(DummyHandler())
        outfile = StringIO()
        with self.assertRaises(TranslatorError):
            trans.write("EN-GB", outfile)

    def test_out_of_quota_raises_exception(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             Start of a movie

             2
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!

             3
             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        trans = SrtTranslator(DummyHandler(in_quota=False, chars=240, limit=250))
        trans.add_input_file(subfile, "EN-GB")
        with self.assertRaises(OutOfQuotaError):
            trans.translate("ROT13")

    def test_empty_in_empty_out(self):
        sf = SubtitleFile()
        trans = SrtTranslator(DummyHandler())
        trans.add_input_srt(sf)
        trans.translate("ROT13")
        self.assertEqual(0, len(list(trans.output["ROT13"])))


if __name__ == "__main__":
    unittest.main()
