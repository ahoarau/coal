:: Find Python executable path for nanobind and Boost.Python
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXECUTABLE=%%i

:: Set default build value only if not previously set
if not defined COAL_BUILD_TYPE (set COAL_BUILD_TYPE=Release)
if not defined COAL_PYTHON_STUBS (set COAL_PYTHON_STUBS=ON)
if not defined COAL_PYTHON_NANOBIND (set COAL_PYTHON_NANOBIND=ON)
if not defined COAL_BUILD_WITH_LOGGING (set COAL_BUILD_WITH_LOGGING=ON)
if not defined COAL_BUILD_WITH_QHULL (set COAL_BUILD_WITH_QHULL=ON)
if not defined COAL_BUILD_WITH_OCTOMAP (set COAL_BUILD_WITH_OCTOMAP=ON)
