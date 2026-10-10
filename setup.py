from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "blighty._x11",
            include_dirs=["/usr/include/cairo/"],
            libraries=["cairo", "X11", "Xinerama"],
            extra_compile_args=["-std=c99"],
            sources=[
                "blighty/x11/_x11module.c",
                "blighty/x11/atelier.c",
                "blighty/x11/base_canvas.c",
            ],
        ),
    ],
)
