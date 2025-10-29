
if(BUILD_TESTING)
  include(FetchContent)
  FetchContent_Declare(
    pytest-cmake
    URL https://github.com/python-cmake/pytest-cmake/archive/refs/tags/1.1.0.zip
    URL_HASH MD5=d3332d7fe077402a83f10d3ab8beaada
  )
  FetchContent_MakeAvailable(pytest-cmake)
  list(APPEND CMAKE_MODULE_PATH ${pytest-cmake_SOURCE_DIR}/cmake)

  xxx_find_package(Pytest REQUIRED)
endif()

pytest_discover_tests(
    coal-tests-all-python
    LIBRARY_PATH_PREPEND
        $<TARGET_FILE_DIR:coal>
        $<TARGET_FILE_DIR:coal_pywrap_nb>
    PYTHON_PATH_PREPEND
        $<TARGET_FILE_DIR:coal_pywrap_nb>/../
    TRIM_FROM_NAME "^(Test|test_)"
    DEPENDS coal_pywrap_nb
    INCLUDE_FILE_PATH
)

