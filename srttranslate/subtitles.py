import re
import pathlib

from collections import namedtuple
from dataclasses import dataclass

subtpline_ptn = r"""
(\d{2})   # start - hour
:
(\d{2})   # start - minute
:
(\d{2})   # start - second
\,
(\d{3})   # start - millisec
\s+
-->
\s+
(\d{2})   # end - hour
:
(\d{2})   # end - minute
:
(\d{2})   # end - second
\,
(\d{3})   # end - millisec
"""

Timepoint = namedtuple("Timepoint", ["hour", "minute", "second", "millisecond"])


def tp_format(tp: Timepoint) -> str:
    return "{0:02}:{1:02}:{2:02},{3:03}".format(*tp)


@dataclass
class SubtitleRecord:
    start: Timepoint
    end: Timepoint
    text: list = None

    def add_line(self, line):
        if self.text is None:
            self.text = []
        self.text.append(line)

    def __str__(self):
        s = f"{tp_format(self.start)} --> {tp_format(self.end)}\n"
        s += "\n".join(self.text or []) + "\n"
        return s


class SubtitleFile:
    def __init__(self):
        self.sublst = []

    def read(self, fil):
        if isinstance(fil, str) or isinstance(fil, pathlib.Path):
            fpath = pathlib.Path(fil)
            fd = fpath.open()
            openedbyus = True
        else:
            try:
                fd = iter(fil)
            except TypeError:
                raise
            openedbyus = False

        try:
            self._read_from_iterable(fd)
        finally:
            if openedbyus:
                fd.close()
        return self

    @staticmethod
    def check_bom(fd):
        c = fd.read(1)
        if c == "\ufeff":
            return
        fd.seek(0)

    def _read_from_iterable(self, fd):
        self.check_bom(fd)
        currentsub = None
        for line in fd:
            line = line.strip()
            if not line:
                if currentsub:
                    self.sublst.append(currentsub)
                currentsub = None
                continue

            if line.isdigit() and not currentsub:
                continue

            m = re.match(subtpline_ptn, line, re.VERBOSE)
            if not m:
                if currentsub:
                    currentsub.add_line(line)
                continue

            if currentsub:
                self.sublst.append(currentsub)

            ints = [int(m.group(i)) for i in range(1, 9)]
            start = Timepoint(*ints[:4])
            end = Timepoint(*ints[4:])
            currentsub = SubtitleRecord(start, end)

        if currentsub:
            self.sublst.append(currentsub)

    def write(self, fd):
        if isinstance(fd, str) or isinstance(fd, pathlib.Path):
            fpath = pathlib.Path(fd)
            fd = fpath.open("w")
            openedbyus = True
        elif hasattr(fd, "write"):
            openedbyus = False
        else:
            raise RuntimeError(
                f"write() needs filename or file-like argument. Got '{fd}'"
            )

        try:
            self._write_to_open_file(fd)
        finally:
            if openedbyus:
                fd.close()
        return self

    def _write_to_open_file(self, fd):
        for i, sub in enumerate(self, 1):
            print(f"{i}\n{sub}", file=fd)

    def __iter__(self):
        class SubtitleIterator:
            def __init__(slf):
                slf.idx = 0

            def __next__(slf):
                if slf.idx >= len(self.sublst):
                    raise StopIteration
                substr = self.sublst[slf.idx]
                slf.idx += 1
                return substr

        return SubtitleIterator()

    def remove_empty_subtitles(self):
        newlist = []
        for sub in self:
            if sub.text:
                newlist.append(sub)
        self.sublst = newlist
        return self

    def count_content_chars(self):
        return sum([len("\n".join(sub.text or "")) for sub in self])
