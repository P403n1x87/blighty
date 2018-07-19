// This file is part of "blighty" which is released under GPL.
//
// See file LICENCE or go to http://www.gnu.org/licenses/ for full license
// details.
//
// blighty is a desktop widget creation and management library for Python 3.
//
// Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
// All rights reserved.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#define BASE_CANVAS_C

#include "atelier.h"
#include "base_canvas.h"

#define PYCAIRO_NO_IMPORT
#include "pycairo.h"
#include "pythread.h"


//
// CONSTANTS
//
#define UI_INTERVAL 1000  // 1 ms

static const char * WINDOW_TYPE_MAP[] = {
  "_NET_WM_WINDOW_TYPE_NORMAL",
  "_NET_WM_WINDOW_TYPE_DESKTOP",
  "_NET_WM_WINDOW_TYPE_DOCK",
  "_NET_WM_WINDOW_TYPE_TOOLBAR"
};


//
// PRIVATE GLOBAL STATE
//
static Display              * display = NULL;
static int                    screen;
static XVisualInfo            visualinfo;
static XSetWindowAttributes   attr;


//
// LOCAL HELPERS
//
static time_t
gettime(void) {
  struct timespec ts;
  clock_gettime(CLOCK_BOOTTIME, &ts);
  return ts.tv_sec * 1000 + ts.tv_nsec / 1e6;
}


static void
BaseCanvas__change_property(BaseCanvas * self, const char * property_name, const char * property_value, int mode) {
  Atom value = XInternAtom(display, property_value, False);
  XChangeProperty(
    display,
    self->win_id,
    XInternAtom(display, property_name, False),
    XA_ATOM,
    32,
    mode,
    (unsigned char *) &value,
    1
  );
}


void
BaseCanvas__redraw(BaseCanvas * self) {
  cairo_save(self->context);
  cairo_set_operator(self->context, CAIRO_OPERATOR_SOURCE);
  cairo_paint(self->context);
  cairo_restore(self->context);
  XFlush(display);
}


void
BaseCanvas__on_draw(BaseCanvas * self, PyObject * args) {
  PyObject * cb = PyObject_GetAttr((PyObject *) self, PyUnicode_FromString("_on_draw"));

  if (cb == NULL) {
    PyErr_SetString(PyExc_TypeError, "Subclasses of BaseCanvas must implement the 'on_draw(self, context)' method.");
    return;
  }
  else {
    if (!PyCallable_Check(cb)) {
      PyErr_SetString(PyExc_TypeError, "on_draw callback must be callable.");
      return;
    }

    // Required for animations in order to avoid flickers.
    // The X server queues up draw requests. This way we group
    // them together and we send a single draw request
    cairo_push_group(self->context);

    // Call user declaration of the 'on_draw' method
    PyObject * cb_result = PyObject_CallObject(cb, args);

    cairo_pattern_t * group = cairo_pop_group(self->context);
    if (cb_result == Py_None)
      cairo_set_source(self->context, group);
    cairo_pattern_destroy(group);
  }
}


static void
BaseCanvas__ui_thread(BaseCanvas * self) {
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  self->context_arg = Py_BuildValue("(O)", PycairoContext_FromContext(self->context, &PycairoContext_Type, (PyObject*) NULL));

  self->_expiry = gettime();

  while (self->_running) {
    Py_BEGIN_ALLOW_THREADS
    usleep(self->interval > 100 ? 100 * UI_INTERVAL : UI_INTERVAL);
    Py_END_ALLOW_THREADS

    if (Atelier_is_running() > 0 && self->_expiry <= gettime()) {
      self->_needs_redraw = 1;

      // Request redraw
      XEvent event;
      event.type = Expose;
      event.xany.window = self->win_id;
      event.xexpose.count = 0;

      XLockDisplay(display);
      XSendEvent(display, self->win_id, False, ExposureMask, &event);
      // Send the event immediately
      XFlush(display);
      XUnlockDisplay(display);

      self->_expiry += self->interval;
    }
  }

  Py_DECREF(self->context_arg);

  PyGILState_Release(gstate);
}


static void
BaseCanvas__transform_coordinates(BaseCanvas * self, int * x, int * y) {
  // TODO: Extend with Xinerama support
  if ((self->gravity - 1) % 3 == 0) *x = self->x;
  else if ((self->gravity - 2) % 3 == 0) *x = ((XDisplayWidth(display, screen) - self->width) >> 1) + self->x;
  else *x = XDisplayWidth(display, screen) - self->width - self->x;

  if (self->gravity <= 3) *y = self->y;
  else if (self->gravity <= 6) *y = ((XDisplayHeight(display, screen) - self->height) >> 1) + self->y;
  else *y = XDisplayHeight(display, screen) - self->height - self->y;
}


//
// class BaseCanvas:
//

//
//    def __del__(self):
//
static void
BaseCanvas_dealloc(BaseCanvas* self) {
  Py_TYPE(self)->tp_free((PyObject*)self);
}


//
//    def __new__(self, *args, **kwargs):
//
static PyObject *
BaseCanvas_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
  BaseCanvas * self;

  self = (BaseCanvas *)type->tp_alloc(type, 0);
  if (self != NULL) {
    char * keywords[] = {"x", "y", "width", "height",
     "interval",        // 1000
     "window_type",     // CanvasType.DESKTOP
     "gravity",         // CanvasGravity.NORTH_WEST
     "sticky",          // True
     "keep_below"       // True
     "skip_taskbar",    // True
     "skip_pager",      // True
     NULL
    };

    // Default keyword arguments
    self->interval   = 1000;
    int window_type  = 1;    // BaseCanvasType.DESKTOP
    self->gravity    = 1;    // BaseCanvasGravity.NORTH_WEST
    int sticky       = 1;
    int keep_below   = 1;
    int skip_taskbar = 1;
    int skip_pager   = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IIII|IIIpppp:BaseCanvas.__new__",
        keywords,
        &self->x, &self->y, &self->width, &self->height,
        &self->interval,
        &window_type,
        &self->gravity,
        &sticky,
        &keep_below,
        &skip_taskbar,
        &skip_pager
       )
    ) return NULL;

    if (display == NULL) {
      if ((display = XOpenDisplay(NULL)) == NULL) return NULL;
      Atelier_set_display(display);
      screen = DefaultScreen(display);

      // Query Visual for "TrueColor" and 32 bits depth (RGBA)
      XMatchVisualInfo(display, screen, 32, TrueColor, &visualinfo);
      attr.colormap = XCreateColormap(display, DefaultRootWindow(display), visualinfo.visual, AllocNone);
      attr.border_pixel = 0;
      attr.background_pixel = 0;
    }

    int x, y;
    BaseCanvas__transform_coordinates(self, &x, &y);

    self->win_id = XCreateWindow(
      display,
      DefaultRootWindow(display),
      x,
      y,
      self->width,
      self->height,
      0,
      visualinfo.depth,
      InputOutput,
      visualinfo.visual,
      CWColormap | CWBorderPixel | CWBackPixel | CWWinGravity,
      &attr
    );

    BaseCanvas__change_property(self, "_NET_WM_WINDOW_TYPE", WINDOW_TYPE_MAP[window_type], PropModeReplace);

    if (keep_below   != 0) BaseCanvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_BELOW"        , PropModeAppend);
    if (sticky       != 0) BaseCanvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_STICKY"       , PropModeAppend);
    if (skip_taskbar != 0) BaseCanvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_SKIP_TASKBAR" , PropModeAppend);
    if (skip_pager   != 0) BaseCanvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_SKIP_PAGER"   , PropModeAppend);

    XCreateGC(display, self->win_id, 0, 0);

    // Handle Delete Event
    self->wm_delete_window = XInternAtom(display, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(display, self->win_id, (Atom *) &(self->wm_delete_window), 1);

    // Create the Cairo Context
    self->surface = cairo_xlib_surface_create(
      display,
      self->win_id,
      visualinfo.visual,
      self->width,
      self->height
    );
    cairo_xlib_surface_set_size(self->surface, self->width, self->height);
    self->context = cairo_create(self->surface);

    self->_running      = 0;
    self->_drawing      = 0;
    self->_needs_redraw = 0;

    // Register the BaseCanvas with the Atelier
    Atelier_add_canvas(self);
  }

  return (PyObject *)self;
}


//
//    def __init__(self, *args, **kwargs):
//
static int
BaseCanvas_init(BaseCanvas *self, PyObject *args, PyObject *kwds)
{
  return 0;
}


//
//    def move(self, x, y):
//      """Move the canvas to new coordinates relative to the current gravity.
//      """
//
static PyObject *
BaseCanvas_move(BaseCanvas * self, PyObject * args, PyObject * kwargs) {
  int new_x, new_y;
  char * keywords[] = {"x", "y", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II:BaseCanvas.move",
    keywords, &new_x, &new_y)
  ) return NULL;

  int x, y;
  self->x = new_x;
  self->y = new_y;
  BaseCanvas__transform_coordinates(self, &x, &y);

  XMoveWindow(display, self->win_id, x, y);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def show(self):
//      """Show the canvas.
//      """
//
static PyObject *
BaseCanvas_show(BaseCanvas* self) {
  // Input events
  XSelectInput(display, self->win_id,
    ButtonPressMask
  | KeyPressMask
  | ExposureMask
  );
  XMapWindow(display, self->win_id);

  self->_running = 1;

  // Use the allocated BaseCanvas object to pass arguments to the UI thread.
  PyThread_start_new_thread((void (*)(void *)) BaseCanvas__ui_thread, self);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def get_size(self):
//      """Get the size of the BaseCanvas.
//
//        Return:
//          (tuple) The `(width, height)` tuple.
//      """
//
static PyObject *
BaseCanvas_get_size(BaseCanvas * self) {
  return Py_BuildValue("(ii)", self->width, self->height);
}


//
//    def dispose(self):
//      """Dispose of the canvas when no longer needed.
//      This method marks the canvas it is called on as ready to be destroyed.
//      The actual destruction is performed by the event loop, which calls the
//      `destroy` method. This is the thread-safe way of destrying an X11
//      BaseCanvas object.
//      """
//
static PyObject *
BaseCanvas_dispose(BaseCanvas * self) {
  XUnmapWindow(display, self->win_id);

  XEvent event;
  event.type = ClientMessage;
  event.xany.window = self->win_id;
	event.xclient.format = 32;
  event.xclient.data.l[0] = self->wm_delete_window;
  XSendEvent(display, self->win_id, True, 0, &event);
  // Send the event immediately
  XFlush(display);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def destroy(self):
//      """Destroy the canvas.
//      WARNING: Not thread-safe. Use `dispose` instead.
//      """
//
static PyObject *
BaseCanvas_destroy(BaseCanvas * self) {
  self->_running = 0;
  cairo_destroy(self->context);
  cairo_surface_destroy(self->surface);

  // De-register BaseCanvas from Atelier;
  if (Atelier_remove_canvas(self) == 0) {
    XCloseDisplay(display);
    display = NULL;
    Atelier_set_display(NULL);
  }

  Py_INCREF(Py_None); return Py_None;
}
