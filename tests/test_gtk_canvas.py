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
