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
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#define BASE_CANVAS_C


#include "atelier.h"
#include "base_canvas.h"

#include <X11/extensions/Xinerama.h>

#define PYCAIRO_NO_IMPORT
#include "pycairo.h"


//
// CONSTANTS
//

static const char * WINDOW_TYPE_MAP[] = {
  "_NET_WM_WINDOW_TYPE_NORMAL",
  "_NET_WM_WINDOW_TYPE_DESKTOP",
  "_NET_WM_WINDOW_TYPE_DOCK",
  "_NET_WM_WINDOW_TYPE_TOOLBAR"
};


//
// PRIVATE GLOBAL STATE
//
static XVisualInfo            visualinfo;
static XSetWindowAttributes   attr;


//
// LOCAL HELPERS
//

// ----------------------------------------------------------------------------
static void
BaseCanvas__change_property(BaseCanvas * self, const char * property_name, const char * property_value, int mode) {
  Display * display = Atelier_get_display();

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


// ----------------------------------------------------------------------------
void
BaseCanvas__redraw(BaseCanvas * self) {
  cairo_save(self->context);
  cairo_set_operator(self->context, CAIRO_OPERATOR_SOURCE);
  cairo_paint(self->context);
  cairo_restore(self->context);
  XFlush(Atelier_get_display());
}


// ----------------------------------------------------------------------------
static void
BaseCanvas__transform_coordinates(BaseCanvas * self, int * x, int * y) {
  Display            * display = Atelier_get_display();
  int                  screen  = DefaultScreen(display);
  XineramaScreenInfo * si      = Atelier_get_screen_info(self->xine_screen);

  int width  = si ? si->width  : XDisplayWidth(display, screen);
  int height = si ? si->height : XDisplayHeight(display, screen);
  int x_org  = si ? si->x_org  : 0;
  int y_org  = si ? si->y_org  : 0;

  if ((self->gravity - 1) % 3 == 0) *x = self->x;
  else if ((self->gravity - 2) % 3 == 0) *x = ((width - self->width) >> 1) + self->x;
  else *x = width - self->width - self->x;
  *x += x_org;

  if (self->gravity <= 3) *y = self->y;
  else if (self->gravity <= 6) *y = ((height - self->height) >> 1) + self->y;
  else *y = height - self->height - self->y;
  *y += y_org;
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
     "screen",          // 0
     "window_type",     // CanvasType.DESKTOP
     "gravity",         // CanvasGravity.NORTH_WEST
     "sticky",          // True
     "keep_below",      // True
     "skip_taskbar",    // True
     "skip_pager",      // True
     NULL
    };

    // Default keyword arguments
    self->interval    = 1000;
    self->xine_screen = 0;
    int window_type   = 1;    // BaseCanvasType.DESKTOP
    self->gravity     = 1;    // BaseCanvasGravity.NORTH_WEST
    int sticky        = 1;
    int keep_below    = 1;
    int skip_taskbar  = 1;
    int skip_pager    = 1;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IIII|IIIIpppp:BaseCanvas.__new__",
        keywords,
        &self->x, &self->y, &self->width, &self->height,
        &self->interval,
        &self->xine_screen,
        &window_type,
        &self->gravity,
        &sticky,
        &keep_below,
        &skip_taskbar,
        &skip_pager
       )
    ) return NULL;

    Display * display = Atelier_get_display();
    if (display == NULL)
      return NULL;

    int screen = DefaultScreen(display);

    // Query Visual for "TrueColor" and 32 bits depth (RGBA)
    XMatchVisualInfo(display, screen, 32, TrueColor, &visualinfo);
    attr.colormap = XCreateColormap(display, DefaultRootWindow(display), visualinfo.visual, AllocNone);
    attr.border_pixel = 0;
    attr.background_pixel = 0;

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

  XMoveWindow(Atelier_get_display(), self->win_id, x, y);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def show(self):
//
static PyObject *
BaseCanvas_show(BaseCanvas* self) {
  Display * display = Atelier_get_display();

  // Input events
  XSelectInput(display, self->win_id,
    ButtonPressMask
  | KeyPressMask
  | ExposureMask
  );
  XMapWindow(display, self->win_id);

  self->_running = 1;

  Py_INCREF(Py_None); return Py_None;
}


//
//    def get_size(self):
//
static PyObject *
BaseCanvas_get_size(BaseCanvas * self) {
  return Py_BuildValue("(ii)", self->width, self->height);
}


//
//    def dispose(self):
//
static PyObject *
BaseCanvas_dispose(BaseCanvas * self) {
  self->_running = 0;
  Display * display = Atelier_get_display();
  XUnmapWindow(display, self->win_id);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def destroy(self):
//
static PyObject *
BaseCanvas_destroy(BaseCanvas * self) {
  self->_running = 0;
  cairo_destroy(self->context);
  cairo_surface_destroy(self->surface);

  Py_INCREF(Py_None); return Py_None;
}


//
//    def _get_context_ptr(self):
//
static PyObject *
BaseCanvas_get_context_ptr(BaseCanvas * self) {
  return PyLong_FromVoidPtr(self->context);
}


//
//    def _get_pycairo_context(self):
//
static PyObject *
BaseCanvas_get_pycairo_context(BaseCanvas * self) {
  cairo_reference(self->context);
  return PycairoContext_FromContext(
    self->context, &PycairoContext_Type, (PyObject *) NULL
  );
}
