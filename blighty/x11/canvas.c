// #include <pthread.h>
#define CANVAS_C

#include "atelier.h"
#include "canvas.h"

#define PYCAIRO_NO_IMPORT
#include "pycairo.h"
#include "pythread.h"

static const char * WINDOW_TYPE_MAP[] = {
  "_NET_WM_WINDOW_TYPE_NORMAL",
  "_NET_WM_WINDOW_TYPE_DESKTOP",
  "_NET_WM_WINDOW_TYPE_DOCK",
  "_NET_WM_WINDOW_TYPE_TOOLBAR"
};

// ---- Class Canvas: methods ------------------------------------------------
static void
Canvas_dealloc(Canvas* self) {
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static void Canvas__change_property(Canvas * self, const char * property_name, const char * property_value, int mode) {
  Atom value = XInternAtom(self->display, property_value, False);
  XChangeProperty(
    self->display,
    self->win_id,
    XInternAtom(self->display, property_name, False),
    XA_ATOM,
    32,
    mode,
    (unsigned char *) &value,
    1
  );
}

static PyObject *
Canvas_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
  Canvas * self;

  self = (Canvas *)type->tp_alloc(type, 0);
  if (self != NULL) {
    char * keywords[] = {"x", "y", "width", "height",
     "interval",        // 1000
     "window_type",     // CanvasType.DESKTOP
     "sticky",          // True
     "keep_below"       // True
     "skip_taskbar",    // True
     "skip_pager",      // True
     "gravity",         // CanvasGravity.NORTH_WEST
     NULL
    };

    // Default keyword arguments
    self->interval   = 1000;
    int window_type  = 1;  // CanvasType.DESKTOP
    int sticky       = 1;
    int keep_below   = 1;
    int skip_taskbar = 1;
    int skip_pager   = 1;
    int gravity      = 1; // CanvasGravity.NORTH_WEST_GRAVITY

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IIII|IIppppI:Canvas.__new__",
        keywords,
        &self->x, &self->y, &self->width, &self->height,
        &self->interval,
        &window_type,
        &sticky,
        &keep_below,
        &skip_taskbar,
        &skip_pager,
        &gravity
       )
    ) return NULL;

    if ((self->display = XOpenDisplay(NULL)) == NULL) return NULL;

    // Query Visual for "TrueColor" and 32 bits depth (RGBA)
    XVisualInfo visualinfo;
    XMatchVisualInfo(self->display, DefaultScreen(self->display), 32, TrueColor, &visualinfo);

    // Create the Window
    XSetWindowAttributes attr;
    attr.colormap = XCreateColormap(self->display, DefaultRootWindow(self->display), visualinfo.visual, AllocNone);
    attr.border_pixel = 0;
    attr.background_pixel = 0;
    attr.win_gravity = gravity;
    // attr.override_redirect = True;
    // attr.event_mask = ExposureMask | StructureNotifyMask | ButtonPressMask | ButtonReleaseMask | Button1MotionMask,

    self->win_id = XCreateWindow(
      self->display,
      DefaultRootWindow(self->display),
      self->x,
      self->y,
      self->width,
      self->height,
      0,
      visualinfo.depth,
      InputOutput,
      visualinfo.visual,
      CWColormap | CWBorderPixel | CWBackPixel | CWWinGravity, // | CWOverrideRedirect | CWEventMask,
      &attr
    );

    // Stick to desktop: DESKTOP
    Canvas__change_property(self, "_NET_WM_WINDOW_TYPE", WINDOW_TYPE_MAP[window_type], PropModeReplace);

    if (keep_below   != 0) Canvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_BELOW"        , PropModeAppend);
    if (sticky       != 0) Canvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_STICKY"       , PropModeAppend);
    if (skip_taskbar != 0) Canvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_SKIP_TASKBAR" , PropModeAppend);
    if (skip_pager   != 0) Canvas__change_property(self, "_NET_WM_STATE", "_NET_WM_STATE_SKIP_PAGER"   , PropModeAppend);

    // TODO: Allow move
    XSelectInput(self->display, self->win_id, StructureNotifyMask);
    XCreateGC(self->display, self->win_id, 0, 0);

    // Handle Delete Event
    self->wm_delete_window = XInternAtom(self->display, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(self->display, self->win_id, (Atom *) &(self->wm_delete_window), 1);

    // Create the Cairo Context
    self->surface = cairo_xlib_surface_create(
      self->display,
      self->win_id,
      visualinfo.visual,
      self->width,
      self->height
    );
    cairo_xlib_surface_set_size(self->surface, self->width, self->height);
    self->context = cairo_create(self->surface);

    self->_running = 0;
    self->_dispose = 0;
    self->_destroy = 0;

    // Register the Canvas with the Atelier
    Atelier_add_canvas(self);
  }

  return (PyObject *)self;
}

static int
Canvas_init(Canvas *self, PyObject *args, PyObject *kwds)
{
  return 0;
}

void
Canvas__on_draw(Canvas * self, PyObject * args) {
  PyObject * cb = PyObject_GetAttr((PyObject *) self, PyUnicode_FromString("on_draw"));
  if (cb == NULL) {
    PyErr_SetString(PyExc_TypeError, "Subclasses of Canvas must implement the 'on_draw(self, context)' method.");
    return;
  }
  else {
    if (!PyCallable_Check(cb)) {
      PyErr_SetString(PyExc_TypeError, "on_draw callback must be callable.");
      return;
    }
    // Required for animations in order to avoid flickers.
    // The X server queues up draw request. This way we group
    // them together and we send a single draw request
    cairo_push_group(self->context);
    // Call user declaration of the 'on_draw' method
    PyObject_CallObject(cb, args);
    cairo_pop_group_to_source(self->context);

    // Only clear the window when we are sure we are ready to paint.
    XClearWindow(self->display, self->win_id);

    cairo_paint(self->context);
  }
}

static void
Canvas__ui_thread(Canvas * self) {
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject *args_tuple = Py_BuildValue("(O)", PycairoContext_FromContext(self->context, &PycairoContext_Type, (PyObject*) NULL));

  while (self->_running) {
    if (self->_dispose != 0) {
      self->_destroy = 1;
      break;
    }
    if (Atelier_is_running() > 0) {
      Canvas__on_draw(self, args_tuple);
    }

    PyGILState_Release(gstate);
    usleep(self->interval * 1000);
    gstate = PyGILState_Ensure();
  }

  Py_DECREF(args_tuple);

  PyGILState_Release(gstate);
}

static PyObject *
Canvas_move (Canvas * self, PyObject * args, PyObject * kwargs) {
  int x, y;
  char * keywords[] = {"x", "y", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II:Canvas.move",
    keywords, &x, &y)
  ) return NULL;

  XMoveWindow(self->display, self->win_id, x, y);

  Py_INCREF(Py_None); return Py_None;
}

static PyObject *
Canvas_show(Canvas* self) {
  // Input events
  XSelectInput(self->display, self->win_id, ButtonPressMask | KeyPressMask);
  XMapWindow(self->display, self->win_id);

  self->_running = 1;

  // Use the allocated Canvas object to pass arguments to the UI thread.
  PyThread_start_new_thread((void (*)(void *)) Canvas__ui_thread, self);

  Py_INCREF(Py_None); return Py_None;
}


static PyObject *
Canvas_get_size(Canvas * self) {
  return Py_BuildValue("(ii)", self->width, self->height);
}


static PyObject *
Canvas_dispose(Canvas * self) {
  self->_dispose = 1;
  Py_INCREF(Py_None); return Py_None;
}


// TODO: With the current design, this method is safe to call only from the
// thread that is running the event loop.
static PyObject *
Canvas_destroy(Canvas * self) {
  self->_running = 0;
  cairo_destroy(self->context);
  cairo_surface_destroy(self->surface);
  XCloseDisplay(self->display);

  // De-register Canvas from Atelier;
  Atelier_remove_canvas(self);

  Py_INCREF(Py_None); return Py_None;
}
