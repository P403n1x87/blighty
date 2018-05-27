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
