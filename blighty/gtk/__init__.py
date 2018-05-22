try:
    import pgi
    pgi.install_as_gi()
except ImportError:
    pass

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from .canvas import Canvas


def start_event_loop():
    Gtk.main()


def stop_event_loop():
    Gtk.main_quit()
