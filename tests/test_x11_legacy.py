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
from blighty import CanvasGravity
from blighty.legacy import Graph
from blighty.x11 import Canvas, start_event_loop


def test_canvas():
    class TestMPL(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            width, height = self.get_size()
            self.plot = Graph(0, 0, width, height >> 1)
            self.refl = Graph(0, height >> 1, width, -(height >> 1))
            self.count = 0

        def on_draw(self, cr):
            cr.set_source_rgb(0.1, 0.1, 0.1)
            cr.rectangle(0, 0, *self.get_size())
            cr.fill()

            v = psutil.cpu_percent(0.1)

            self.plot.push_value(v)
            self.refl.push_value(v)

            cr.set_source_rgb(1, 1, 1)
            self.plot.draw(cr)
            cr.set_source_rgb(.2, .2, .2)
            self.refl.draw(cr)
            self.count += 1

            if self.count > 300:
                self.dispose()

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        def on_key_pressed(self, keysym, state):
            if keysym == 65307:
                self.dispose()

    canvas = TestMPL(10, 10, 160, 160, gravity = CanvasGravity.SOUTH_EAST)
    canvas.interval = 500
    canvas.show()
    start_event_loop()


if __name__ == "__main__":
    test_canvas()
