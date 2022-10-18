AC_INIT([xdp], [0.1])

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([3])

AX_PYTHON_MODULE([certifi], [true])
AX_PYTHON_MODULE([colorama], [true])
AX_PYTHON_MODULE([humanize], [true])
AX_PYTHON_MODULE([packaging], [true])
AX_PYTHON_MODULE([pycurl], [true])
AX_PYTHON_MODULE([toml], [true])

AC_CONFIG_FILES([
Makefile
libxdp/Makefile
libxdp/__init__.py
libxdp/pkg/Makefile
libxdp/pkg/build/Makefile
])
AC_OUTPUT
