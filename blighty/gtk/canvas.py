"""
This file is part of "blighty" which is released under GPL.

See file LICENCE or go to http://www.gnu.org/licenses/ for full license
details.

blighty is a desktop widget creation and management library for Python 3.

Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
                 gravity = CanvasGravity.NORTH_WEST,
                 sticky = True,
                 keep_below = True,
                 skip_taskbar = True,
                 skip_pager = True
                 ):

        super().__init__()

        self.interval = interval
        self.gravity = gravity

        self.set_type_hint(WINDOW_TYPE_MAP[window_type])

        if skip_taskbar:
            self.set_skip_taskbar_hint(True)

        if skip_pager:
            self.set_skip_pager_hint(True)

        if sticky:
            self.stick()

        if keep_below:
            self.set_keep_below(keep_below)

        self.screen = self.get_screen()

        self.width = width
        self.height = height
        self.set_size_request(width, height)
        self.move(x, y)

        # Handle gravity with respect to parent window manually
        self.set_gravity(gravity)

        # Make the window transparent
        visual = self.screen.get_rgba_visual()
        if visual is not None and self.screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)

        # Connect signals
        self.connect("draw", self._on_draw)
        self.connect("delete-event", Gtk.main_quit)

    def _translate_coordinates(self, x, y):
        if (self.gravity - 1) % 3 == 0:
            tx = x
        elif (self.gravity - 2) % 3 == 0:
            tx = ((self.screen.get_width() - self.width) >> 1) + x
        else:
            tx = self.screen.get_width() - self.width - x

        if self.gravity <= 3:
            ty = y
        elif self.gravity <= 6:
            ty = ((self.screen.get_height() - self.height) >> 1) + y
        else:
            ty = self.screen.get_height() - self.height - y

        return tx, ty

    def _on_draw(self, widget, cr):
        # Call draw method from subclass
        self.on_draw(widget, cr)

        # Request redraw
        widget.queue_draw()

        sleep(self.interval / 1000.)

    def on_draw(self, widget, cr):
        raise NotImplementedError("on_draw method not implemented in subclass.")

    def request_redraw(self):
        self.queue_draw()

    def show(self):
        self.show_all()

    def move(self, x, y):
        self.x = x
        self.y = y
        return super().move(*self._translate_coordinates(x, y))
