try:
    import pgi
    pgi.install_as_gi()
except ImportError:
    pass

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

import cairo

class Canvas(Gtk.Window):

    def __init__(self, width, height, opacity = 0.0, sticky = True, keep_below = True):
        super().__init__()
        self.connect("delete-event", Gtk.main_quit)
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        if sticky:
            self.stick()
        self.set_keep_below(keep_below)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.width = width
        self.height = height
        self.set_size_request(width, height)

        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual is not None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.set_app_paintable(True)
        self.opacity = opacity
        self.connect("draw", self._on_draw)

    def _on_draw(self, widget, cr):
        cr.set_source_rgba(.2, .2, .2, self.opacity)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        self.on_draw(widget, cr)

    def on_draw(self, widget, cr):
        pass

    def request_redraw(self):
        self.queue_draw()
