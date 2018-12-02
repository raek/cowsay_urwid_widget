from functools import lru_cache
import urwid
from subprocess import Popen, PIPE


class Cowsay(urwid.Overlay):

    def __init__(self, top_w):
        super().__init__(
            top_w, _Cow(),
            align='left', width=('relative', 100),
            valign='top', height=('relative', 100),
            **_Cow.PADDING
        )


class _Cow(urwid.Widget):

    ignore_focus = True
    _selectable = False

    PADDING = dict(
        left=2,
        right=2,
        top=1,
        bottom=6
    )

    def _inner_size(self, size):
        maxcol, maxrow = size
        inner_maxcol = maxcol - self.PADDING['left'] - self.PADDING['right']
        inner_maxrow = maxrow - self.PADDING['top'] - self.PADDING['bottom']
        return inner_maxcol, inner_maxrow

    def _cow_lines(self, size):
        inner_maxcol, inner_maxrow = size
        dummy_line = inner_maxcol * "#"
        dummy_box = "\n".join(inner_maxrow * [dummy_line])
        p = Popen(["cowsay", "-W", str(inner_maxcol + 1)], stdin=PIPE, stdout=PIPE)
        cow_text = p.communicate(dummy_box.encode("utf-8"))[0]
        assert p.returncode == 0
        return cow_text.splitlines()

    def render(self, size, focus=False):
        lines = self._cow_lines(self._inner_size(size))
        return urwid.TextCanvas(lines, maxcol=size[0])

    def sizing(self):
        return frozenset(['box'])


if __name__ == '__main__':
    def exit_loop(*args, **kwargs):
        raise urwid.ExitMainLoop()
    cowsay = Cowsay(urwid.SolidFill(' '))
    background = urwid.SolidFill(' ')
    placement = urwid.Overlay(cowsay, background, align='center', width=('relative', 75), valign='bottom', height=('relative', 75))
    loop = urwid.MainLoop(placement)
    terminal = urwid.Terminal(None, main_loop=loop)
    urwid.connect_signal(terminal, 'closed', exit_loop)
    cowsay.top_w = terminal
    loop.run()
