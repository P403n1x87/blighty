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

import psutil

from blighty.gtk import Canvas, start_event_loop, stop_event_loop
from blighty import CanvasGravity
from plot import SimplePlot


class MPL(Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = SimplePlot(self.width, self.height)
        self.count = 0

    def on_draw(self, widget, cr):
        self.plot.push_value(psutil.cpu_percent(2))
        self.plot.draw(cr)
        widget.request_redraw()

        self.count += 1
        if self.count > 10:
            self.destroy()
            stop_event_loop()


def test_gtk_canvas():
    canvas = MPL(100, 100, width = 320, height = 160, gravity = CanvasGravity.SOUTH_EAST)
    canvas.show()
    start_event_loop()
