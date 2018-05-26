try:
    import gi
except ImportError:
    raise ImportError("Unable to import PyGObject. See https://pygobject.readthedocs.io/ for more info.")

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from .canvas import Canvas


def start_event_loop():
    Gtk.main()


def stop_event_loop():
    Gtk.main_quit()
