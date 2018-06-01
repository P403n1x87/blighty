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

from blighty.x11 import Canvas, start_event_loop
from blighty import CanvasGravity

import psutil
from plot import SimplePlot

def test_canvas():
    class TestMPL(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.plot = SimplePlot(*self.get_size())
            self.count = 5

        def on_draw(self, cr):
            self.plot.push_value(psutil.cpu_percent(2))
            self.plot.draw(cr)
            self.count += 1

            if self.count > 10:
                self.dispose()

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.destroy()

        def on_key_pressed(self, keysym, state):
            if keysym == 65307:
                self.destroy()

    canvas = TestMPL(10, 10, 320, 160, gravity = CanvasGravity.SOUTH_EAST)
    canvas.interval = 0
    canvas.show()
    start_event_loop()


if __name__ == "__main__":
    test_canvas()
