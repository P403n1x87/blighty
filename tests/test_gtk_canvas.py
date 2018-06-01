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

import blighty.gtk as b
from blighty import CanvasGravity


class MyCanvas(b.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.r = 50.0
        self.d = 1.0

    def on_draw(self, widget, cr):
        cr.set_line_width(8)
        cr.set_source_rgba(0.7, 0.2, 0.0, .5)

        w, h = self.get_size()

        if self.r > 92 or self.r < 10:
            self.d *= -1
        self.r += self.d

        cr.arc(w >> 1, h >> 1, self.r, 0, 2 * 3.14159265)
        cr.stroke_preserve()

        cr.set_source_rgba(0.3, 0.4, 0.6, .5)
        cr.fill()

        if self.r == 10:
            self.destroy()
            b.stop_event_loop()


def test_gtk_canvas():
    canvases = [MyCanvas(200 * i, 200 * i, 200, 200, gravity = CanvasGravity.CENTER) for i in range(-1,2)]

    for canvas in canvases:
        assert canvas.interval == 1000

        canvas.interval = 10
        assert canvas.show() is None

    b.start_event_loop()
