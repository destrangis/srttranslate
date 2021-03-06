import unittest
from io import StringIO
from textwrap import dedent

from srttranslate.subtitles import SubtitleFile


class SubtitleTest(unittest.TestCase):
    def test_good_subs_read(self):
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
            "00:00:00,500 --> 00:00:03,000\nStart of a movie\n",
            "00:01:12,629 --> 00:01:15,183\n"
            "- Hello, Ms. Wilkins!\n"
            "- Good morning!\n",
            "00:01:17,321 --> 00:01:19,742\n" "No, use the other door, please\n",
        ]

        sf = SubtitleFile().read(subfile)
        self.assertEqual(3, len(list(sf)))
        for sub, exp in zip(sf, expected):
            self.assertEqual(str(sub), exp)

    def test_unnumbered_subs_read(self):
        subfile = StringIO(
            dedent(
                """
             00:00:00,500 --> 00:00:03,000
             Start of a movie

             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!

             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        expected = [
            "00:00:00,500 --> 00:00:03,000\nStart of a movie\n",
            "00:01:12,629 --> 00:01:15,183\n"
            "- Hello, Ms. Wilkins!\n"
            "- Good morning!\n",
            "00:01:17,321 --> 00:01:19,742\n" "No, use the other door, please\n",
        ]

        sf = SubtitleFile().read(subfile)
        self.assertEqual(3, len(list(sf)))
        for sub, exp in zip(sf, expected):
            self.assertEqual(str(sub), exp)

    def test_nonsub_lines_ignored(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             Start of a movie

             - Hello, Ms. Wilkins!
             - Good morning!

             3
             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        expected = [
            "00:00:00,500 --> 00:00:03,000\nStart of a movie\n",
            "00:01:17,321 --> 00:01:19,742\n" "No, use the other door, please\n",
        ]

        sf = SubtitleFile().read(subfile)
        self.assertEqual(2, len(list(sf)))
        for sub, exp in zip(sf, expected):
            self.assertEqual(str(sub), exp)

    def test_really_bad_subs_read(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!


             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
        """
            )
        )
        expected = [
            "00:00:00,500 --> 00:00:03,000\n\n",
            "00:01:12,629 --> 00:01:15,183\n"
            "- Hello, Ms. Wilkins!\n"
            "- Good morning!\n",
            "00:01:17,321 --> 00:01:19,742\n" "No, use the other door, please\n",
        ]

        sf = SubtitleFile().read(subfile)
        self.assertEqual(3, len(sf.sublst))
        for sub, exp in zip(sf, expected):
            self.assertEqual(str(sub), exp)

    def test_write_good_subs(self):
        expected = (
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
            ).strip()
            + "\n\n"
        )
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

        outfile = StringIO()
        sf = SubtitleFile().read(subfile)
        sf.write(outfile)
        self.assertEqual(outfile.getvalue(), expected)

    def test_remove_empty_subs(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!


             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
        """
            )
        )
        expected = [
            "00:01:12,629 --> 00:01:15,183\n"
            "- Hello, Ms. Wilkins!\n"
            "- Good morning!\n",
            "00:01:17,321 --> 00:01:19,742\n" "No, use the other door, please\n",
        ]
        sf = SubtitleFile().read(subfile).remove_empty_subtitles()
        self.assertEqual(2, len(sf.sublst))
        for sub, exp in zip(sf, expected):
            self.assertEqual(str(sub), exp)

    def test_count_chars_normal(self):
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
        sf = SubtitleFile().read(subfile)
        self.assertEqual(83, sf.count_content_chars())

    def test_count_chars_empty_subfile(self):
        sf = SubtitleFile()
        self.assertEqual(0, sf.count_content_chars())

    def test_count_chars_empty_subs(self):
        subfile = StringIO(
            dedent(
                """
             1
             00:00:00,500 --> 00:00:03,000
             00:01:12,629 --> 00:01:15,183
             - Hello, Ms. Wilkins!
             - Good morning!


             00:01:17,321 --> 00:01:19,742
             No, use the other door, please
             """
            )
        )
        sf = SubtitleFile().read(subfile)
        self.assertEqual(67, sf.count_content_chars())


if __name__ == "__main__":
    unittest.main()
