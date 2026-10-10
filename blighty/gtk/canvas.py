# This file is part of "blighty" which is released under GPL.
#
# See file LICENCE or go to http://www.gnu.org/licenses/ for full license
# details.
#
# blighty is a desktop widget creation and management library for Python 3.
#
# Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""GTK backend for blighty widgets.

GTK runs on the main thread.  An asyncio event loop runs in a background
thread for handling async widget callbacks.  Canvas operations are
marshalled to GTK via ``GLib.idle_add()``.
"""

try:
    import gi
except ImportError:
    raise ImportError(
        "Unable to import PyGObject. See https://pygobject.readthedocs.io/"
    )

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from blighty import CanvasGravity, CanvasType
from blighty._extended_context import ExtendedContext
from gi.repository import Gdk, Gtk, GLib

import asyncio
import threading

WINDOW_TYPE_MAP = [
    Gdk.WindowTypeHint.NORMAL,
    Gdk.WindowTypeHint.DESKTOP,
    Gdk.WindowTypeHint.DOCK,
    Gdk.WindowTypeHint.TOOLBAR,
]

# The asyncio event loop running in a background thread
_async_loop = None
_async_thread = None


class Canvas(Gtk.Window):
    """GTK canvas adapter.

    Wraps a :class:`~blighty.Widget` subclass as a ``Gtk.Window``.
    Users should not instantiate this directly.
    """

    def __init__(self, widget):
        super().__init__()

        self._widget = widget
        widget._canvas = self
        self._extended_context = None

        self.set_type_hint(WINDOW_TYPE_MAP[widget.__window_type__])

        if widget.__skip_taskbar__:
            self.set_skip_taskbar_hint(True)
        if widget.__skip_pager__:
            self.set_skip_pager_hint(True)
        if widget.__sticky__:
            self.stick()
        if widget.__keep_below__:
            self.set_keep_below(True)

        screen = self.get_screen()
        self.width = widget.__width__
        self.height = widget.__height__
        self.set_size_request(self.width, self.height)
        self.xine_screen = widget.__screen__
        self.gravity = widget.__gravity__

        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self._translate_and_move(widget.__x__, widget.__y__)

        self.connect("draw", self._on_draw)
        self.connect("delete-event", self._on_delete)
        self.connect("button-press-event", self._on_button_press)
        self.connect("key-press-event", self._on_key_press)

    def _translate_and_move(self, x, y):
        screen = self.get_screen()
        if self.xine_screen < 0 or self.xine_screen >= screen.get_n_monitors():
            w = screen.get_width()
            h = screen.get_height()
            x_org = 0
            y_org = 0
        else:
            mon = screen.get_monitor_geometry(self.xine_screen)
            w = mon.width
            h = mon.height
            x_org = mon.x
            y_org = mon.y

        g = self.gravity
        if (g - 1) % 3 == 0:
            tx = x
        elif (g - 2) % 3 == 0:
            tx = ((w - self.width) >> 1) + x
        else:
            tx = w - self.width - x

        if g <= 3:
            ty = y
        elif g <= 6:
            ty = ((h - self.height) >> 1) + y
        else:
            ty = h - self.height - y

        self.move(tx + x_org, ty + y_org)

    def _schedule_coro(self, coro):
        if _async_loop is not None and _async_loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, _async_loop)

    def _on_draw(self, widget, cr):
        self._extended_context = ExtendedContext(cr, self._widget)
        self._schedule_coro(self._widget.draw(self._extended_context))

    def _on_button_press(self, widget, event):
        self._schedule_coro(self._widget.on_button_pressed(
            event.button, event.state, event.x, event.y
        ))

    def _on_key_press(self, widget, event):
        self._schedule_coro(self._widget.on_key_pressed(
            event.keyval, event.state
        ))

    def _on_delete(self, widget, event):
        self._widget._running = False
        Gtk.main_quit()

    def show(self):
        """Map the canvas to screen and start the periodic refresh timer."""
        self.show_all()
        self._widget._running = True
        GLib.timeout_add(self._widget.__interval__, self._refresh_tick)
        return self

    def _refresh_tick(self):
        if not self._widget._running:
            return False
        self._schedule_coro(self._widget._tick())
        return True

    def get_size(self):
        return (self.width, self.height)

    def dispose(self):
        self._widget._running = False
        GLib.idle_add(Gtk.main_quit)

    def destroy(self):
        self._widget._running = False
        Gtk.Window.destroy(self)


def create_canvas(widget):
    """Create and return a GTK Canvas wrapping the given Widget."""
    return Canvas(widget)


def start_event_loop():
    """Start GTK main loop with asyncio in a background thread."""
    global _async_loop, _async_thread

    ready = threading.Event()

    def _run_async():
        global _async_loop
        _async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_async_loop)
        ready.set()
        _async_loop.run_forever()

    _async_thread = threading.Thread(target=_run_async, daemon=True)
    _async_thread.start()
    ready.wait()

    Gtk.main()


def stop_event_loop():
    """Stop the GTK main loop."""
    Gtk.main_quit()
