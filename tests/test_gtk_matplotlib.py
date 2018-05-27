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
