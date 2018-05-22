import blighty.x11
print(dir(blighty.x11))

# from blighty.x11 import Canvas, start_event_loop
#
# import psutil
# from blighty.gtk.plot import SimplePlot
#
# def test_canvas():
#     class TestMPL(Canvas):
#         def __init__(self, x, y, w, h):
#             super().__init__(x, y, w, h)
#
#             self.plot = SimplePlot(w, h)
#
#         def on_draw(self, cr):
#             self.plot.push_value(psutil.cpu_percent(2))
#             self.plot.draw(cr)
#
#         def on_button_pressed(self, button, state, x, y):
#             if button == 1:
#                 self.destroy()
#
#         def on_key_pressed(self, keysym, state):
#             if keysym == 65307:
#                 self.destroy()
#
#     canvas = TestMPL(0, 0, 320, 160)
#     canvas.interval = 1e8
#     canvas.show()
#     start_event_loop()
#
#
# if __name__ == "__main__":
#     test_canvas()
