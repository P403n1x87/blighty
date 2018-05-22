from numpy import arange

from matplotlib.backends.backend_gtk3cairo import RendererGTK3Cairo
from matplotlib.figure import Figure


class MockCanvas:
    __slots__ = []

    def is_saving(self):
        return False

    def draw_event(self, renderer):
        pass


class SimplePlot:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.values = [-1] * 100

    def push_value(self, v):
        self.values.pop(0)
        self.values.append(v)

    def draw(self, cr):
        dpi = 96
        f = Figure(figsize=(self.width / dpi, self.height / dpi), dpi=dpi)
        ax = f.add_subplot(111)
        t = arange(0, 100, 1)
        s = self.values
        f.set_facecolor((0, 0, 0, 0))
        ax.set_facecolor((0, 0, 0, 0))
        f.subplots_adjust(wspace=0, top=1.0, bottom=0.0, left=0, right=1.0)

        ax.axis('off')
        ax.set_ylim([0, 100])

        ax.fill_between(t, s, [0] * 100)

        renderer = RendererGTK3Cairo(f.dpi)
        renderer.set_context(cr)
        renderer.set_width_height(self.width, self.height)

        f.canvas = MockCanvas()  # Monkey patch to reduce memory footprint.
        f.draw(renderer)
