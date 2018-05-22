import blighty.gtk as b


class MyCanvas(b.Canvas):

    def on_draw(self, widget, cr):
        cr.set_line_width(9)
        cr.set_source_rgb(0.7, 0.2, 0.0)

        w, h = self.get_size()

        cr.translate(w >> 1, h >> 1)
        cr.arc(0, 0, 50, 0, 2*3.14159265)
        cr.stroke_preserve()

        cr.set_source_rgb(0.3, 0.4, 0.6)
        cr.fill()

        self.destroy()
        b.stop_event_loop()


def test_gtk_canvas():
    canvas = MyCanvas(width=320, height=240)
    canvas.show_all()
    b.start_event_loop()
