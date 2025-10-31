# Copyright 2025 INRIA

set(
  PYWRAP_HEADERS
  broadphase/broadphase_callbacks_collision_manager.hh
  fwd.h
  pickle.hh
  serializable.hh
)

set(
  PYWRAP_SOURCES
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
  list(APPEND PYWRAP_SOURCES octree.cc)
endif()

nanobind_add_module(coal_pywrap_nb NB_STATIC LTO NB_SUPPRESS_WARNINGS ${PYWRAP_SOURCES} ${PYWRAP_HEADERS})
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


xxx_python_compile_files(
  FILES coal/__init__.py
        coal/windows_dll_manager.py
  GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}
)
