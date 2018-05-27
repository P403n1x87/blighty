def test_canvas():
    import blighty.x11 as x11
    from blighty import CanvasGravity

    class MyCanvas(x11.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.r = 50.0
            self.d = 1.0

        def on_button_pressed(self, button, state, x, y):
            if button == 1 and state == 0:
                self.destroy()

        def on_key_pressed(self, keysym, state):
            if keysym == 65307:
                self.destroy()

        def on_draw(self, cr):
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
                self.dispose()

    canvases = [MyCanvas(200 * i, 200 * i, width = 200, height = 200, interval = 42, gravity = CanvasGravity.CENTER) for i in range(-1, 2)]

    for canvas in canvases:
        assert canvas.interval == 42

        canvas.interval = 50
        assert canvas.show() is None

    assert x11.start_event_loop() is None


if __name__ == "__main__":
    test_canvas()
