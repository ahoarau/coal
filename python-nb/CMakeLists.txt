# Copyright 2025 INRIA

# Headers
set(
  PYTHON_LIB_HEADERS
  broadphase/broadphase_callbacks_collision_manager.hh
  fwd.h
  pickle.hh
  serializable.hh
)

# Sources
set(
  PYTHON_LIB_SOURCES
  broadphase/broadphase.cc
  aabb.cc
  bvh.cc
  collision-geometries.cc
  collision.cc
  contact_patch.cc
  distance.cc
  math.cc
  gjk.cc
  height_field.cc
  memory-footprint.cc
  shapes.cc
  module.cc
)
if(COAL_HAS_OCTOMAP)
  list(APPEND PYTHON_LIB_SOURCES octree.cc)
endif()

nanobind_add_module(coal_pywrap_nb NB_STATIC LTO NB_SUPPRESS_WARNINGS ${PYTHON_LIB_SOURCES})
install(TARGETS coal_pywrap_nb 
  EXPORT coal-coal 
  LIBRARY DESTINATION ${Python_SITELIB}/coal
)
target_link_libraries(
  coal_pywrap_nb
  PRIVATE coal Boost::boost
)
target_compile_definitions(
  coal_pywrap_nb
  PRIVATE COAL_PYTHON_LIBNAME=coal_pywrap_nb
)

set_target_properties(
  coal_pywrap_nb
  PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/coal
)

nanobind_add_stub(
  coal_pywrap_nb_stub
  VERBOSE
  MODULE coal
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/coal/coal_pywrap_nb.pyi
  PYTHON_PATH $<TARGET_FILE_DIR:coal_pywrap_nb>
  DEPENDS coal_pywrap_nb
)
install(
  FILES coal/coal_pywrap_nb.pyi
  DESTINATION ${Python_SITELIB}/coal
)
add_dependencies(coal_python coal_pywrap_nb)

function(xxx_python_compile_file)
    set(options)
    set(oneValueArgs INPUT GEN_DIR DESTINATION)
    set(multiValueArgs)
    cmake_parse_arguments(PARSE_ARGV 0 arg "${options}" "${oneValueArgs}" "${multiValueArgs}")

    xxx_require_variable(Python_EXECUTABLE)

    xxx_require_variable(arg_INPUT)
    xxx_require_variable(arg_GEN_DIR)
    xxx_require_variable(arg_DESTINATION)

    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "import py_compile; print(py_compile.compile(r'${arg_INPUT}', doraise=True), end='')"
        OUTPUT_VARIABLE compiled_file
        RESULT_VARIABLE result
    )

    message(STATUS "Compiled Python file '${arg_INPUT}' to '${compiled_file}'")
    cmake_path(CONVERT ${compiled_file} TO_CMAKE_PATH_LIST compiled_file NORMALIZE)
    cmake_path(GET compiled_file FILENAME output_filename)

    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Failed to compile Python file '${arg_INPUT}'")
    endif()

    file(COPY ${arg_INPUT} DESTINATION ${arg_GEN_DIR})
    file(COPY ${compiled_file} DESTINATION ${arg_GEN_DIR}/__pycache__)
    set_source_files_properties(${compiled_file} PROPERTIES GENERATED True)

    install(
      FILES ${compiled_file}
      DESTINATION ${arg_DESTINATION}
    )
endfunction()


xxx_python_compile_file(
  INPUT ${CMAKE_CURRENT_SOURCE_DIR}/coal/__init__.py
  GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/coal
  DESTINATION ${Python_SITELIB}/coal
)

xxx_python_compile_file(
  INPUT ${CMAKE_CURRENT_SOURCE_DIR}/coal/windows_dll_manager.py
  GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/coal
  DESTINATION ${Python_SITELIB}/coal
)
