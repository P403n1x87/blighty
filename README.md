# blighty

## Synopsis

The **blighty** project is inspired by conky. In essence, it is a collection of
objects that allow you to quickly create a transparent window that you can draw
on with cairo. But instead of coding your widgets in Lua, that perhaps end up
calling Python as external tools, you can now code them natively in Python.

Performance won't be as great as conky, with probably more resource being used
for the same end result, but native Python support opens up for a lot more
customisation possibilities in a snap of your fingers.

There won't be much you can do with minimal effort out of the box while the
project is in its infancy. If you like the idea, you are more than welcome to
contribute to this project!

## Requirements

- Xlib (only for X Windows)
- cairo
- python3
- python3-gi (only for GTK Windows)
- gir1.2-gtk-3.0 (only for GTK Windows)
- gir1.2-glib-2.0 (only for GTK Windows)


## Installation

### Ubuntu

Make sure that all dependencies are satisfied:

~~~
sudo apt install python3-gi, gir1.2-gtk-3.0, gir1.2-glib-2.0
~~~

Clone this branch in any folder you like and then run the `setup.py` script with

~~~
sudo -H python3 -m pip install .
~~~


## Usage

Refer to the code in the `tests` folder for some simple examples.

This package makes it easy to create transparent windows that you can draw on
with `cairo`. It takes all the boilerplate code away from you so that you can
just focus on the artwork, pretty much as with conky.

### Creating X11 Canvases

This is the closest to conky that you can get for the moment. Use the following
approach to create a window with the Xlib directly.

~~~ python
from blighty.x11 import Canvas, start_event_loop

class MyCanvas(Canvas):
  def on_draw(self, context):
    # context is an instance of a cairo context.
    # Refer to the Pycairo documentation.
    #
if __name__ == "__main__":
  x, y, width, height = 10, 10, 200, 200

  # Instantiate the canvas
  canvas = MyCanvas(x, y, width, height)

  # Map it on screen
  canvas.show()

  # Start the event loop
  start_event_loop()
~~~

The module implements a basic event loop so that the user interactions with the
canvas can be handled. You can capture key and button presses by implementing
the `on_key_pressed(self, keysym, state)` and `on_button_pressed(self, button,
state, x, y)` method in your subclass of `Canvas`.

### Creating GTK Windows

To create GTK-based canvases you can use the `blighty.gtk.Canvas` class, which
is just a subclass of `Gtk.Window`.

~~~ python
from time import sleep
import blighty.gtk as b


class MyCanvas(b.Canvas):
    def on_draw(self, widget, cr):
        # Similar to the X11 case. However, note how
        # you have access to the whole GTK window
        # via the `widget` parameter. In principle you
        # can exploit it to add extra child widgets.
        # Use wisely.

if __name__ == "__main__":
    canvas = MyCanvas(width=320, height=240)
    canvas.show_all()
    b.start_event_loop()
~~~

## License

GPLv3.
