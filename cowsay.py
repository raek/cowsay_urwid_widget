import urwid
from subprocess import Popen, PIPE


class Cowsay(urwid.WidgetDecoration):

    _LEFT = 2
    _RIGHT = 2
    _TOP = 1
    _BOTTOM = 6

    def _inner_size(self, size):
        maxcol, maxrow = size
        inner_maxcol = maxcol - self._LEFT - self._RIGHT
        inner_maxrow = maxrow - self._TOP - self._BOTTOM
        return inner_maxcol, inner_maxrow

    def _cow_lines(self, inner_size):
        inner_maxcol, inner_maxrow = inner_size
        dummy_line = inner_maxcol * "#"
        dummy_box = "\n".join(inner_maxrow * [dummy_line])
        p = Popen(["cowsay", "-W", str(inner_maxcol + 1)], stdin=PIPE, stdout=PIPE)
        cow_text = p.communicate(dummy_box.encode("utf-8"))[0].decode("utf-8")
        assert p.returncode == 0
        return [line.encode("utf-8") for line in cow_text.splitlines()]

    def render(self, size, focus=False):
        inner_size = self._inner_size(size)
        lines = self._cow_lines(inner_size)
        cow = urwid.TextCanvas(lines, maxcol=size[0])
        inner = self.original_widget.render(inner_size, focus)
        return urwid.CanvasOverlay(urwid.CompositeCanvas(inner), cow, self._LEFT, self._TOP)

    def keypress(self, size, key):
        return self.original_widget.keypress(self._inner_size(size), key)

    def mouse_event(self, size, event, button, col, row, focus):
        if not hasattr(self.original_widget, 'mouse_event'):
            return False
        return self.original_widget.mouse_event(self._inner_size(size), event, button, col - self._LEFT, row - self._TOP, focus)

    def get_cursor_coords(self, size):
        if not hasattr(self.original_widget, 'get_cursor_coords'):
            return None
        coords = self.original_widget.get_cursor_coords(self._inner_size(size))
        if not coords:
            return None
        col, row = coords
        return col + self._LEFT, row + self._TOP

    def get_pref_col(self, size):
        if not hasattr(self.original_widget, 'get_pref_col'):
            return 'left'
        col = self.original_widget.get_pref_col(self._inner_size(size))
        if isinstance(col, int):
            return col + self._LEFT
        else:
            return col

    def move_cursor_to_coords(self, size, col, row):
        if not hasattr(self.original_widget, 'get_pref_col'):
            return False
        return self.original_widget.move_cursor_to_coords(self._inner_size(size), col - self._LEFT, row - self._TOP)

    def selectable(self):
        return self.original_widget.selectable()

    def sizing(self):
        return frozenset(['box'])


if __name__ == '__main__':
    def exit_loop(*args, **kwargs):
        raise urwid.ExitMainLoop()
    cowsay = Cowsay(urwid.SolidFill(' '))
    background = urwid.SolidFill(' ')
    overlay = urwid.Overlay(cowsay, background, align='center', width=('relative', 75), valign='bottom', height=('relative', 75))
    loop = urwid.MainLoop(overlay)
    terminal = urwid.Terminal(None, main_loop=loop)
    urwid.connect_signal(terminal, 'closed', exit_loop)
    cowsay.original_widget = terminal
    loop.run()
