try:
    import gi
except ImportError:
    raise ImportError("Unable to import PyGObject. See https://pygobject.readthedocs.io/ for more info.")

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

import cairo

from time import sleep
from blighty import CanvasType, CanvasGravity

WINDOW_TYPE_MAP = [
    Gdk.WindowTypeHint.NORMAL,
    Gdk.WindowTypeHint.DESKTOP,
    Gdk.WindowTypeHint.DOCK,
    Gdk.WindowTypeHint.TOOLBAR,
]

class Canvas(Gtk.Window):

    def __init__(self, x, y, width, height,
                 interval = 1000,
                 window_type = CanvasType.DESKTOP,
                 sticky = True,
                 keep_below = True,
                 skip_taskbar = True,
                 skip_pager = True,
                 gravity = CanvasGravity.NORTH_WEST
                 ):

        super().__init__()

        self.connect("delete-event", Gtk.main_quit)

        self.set_type_hint(WINDOW_TYPE_MAP[window_type])

        if skip_taskbar:
            self.set_skip_taskbar_hint(True)

        if skip_pager:
            self.set_skip_pager_hint(True)

        if sticky:
            self.stick()

        if keep_below:
            self.set_keep_below(keep_below)

        self.gravity = gravity

        self.width = width
        self.height = height
        self.set_size_request(width, height)
        self.move(x, y)

        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual is not None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.set_app_paintable(True)
        self.connect("draw", self._on_draw)

        self.interval = interval

    def _on_draw(self, widget, cr):
        self.on_draw(widget, cr)
        widget.request_redraw()
        sleep(self.interval / 1000.)

    def on_draw(self, widget, cr):
        pass

    def request_redraw(self):
        self.queue_draw()

    def show(self):
        self.show_all()
