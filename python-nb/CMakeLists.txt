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
xxx_target_enforce_msvc_conformance(coal_pywrap_nb PRIVATE)
target_link_libraries(
  coal_pywrap_nb
  PRIVATE coal
)
set_target_properties(
  coal_pywrap_nb
  PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/site-packages/coal
)

xxx_python_generate_init_py(
    coal_pywrap_nb
    OUTPUT_PATH ${CMAKE_BINARY_DIR}/lib/site-packages/coal/__init__.py
)

nanobind_add_stub(
  coal_pywrap_nb_stub
  VERBOSE
  MODULE coal
  OUTPUT ${CMAKE_BINARY_DIR}/lib/site-packages/coal/coal_pywrap_nb.pyi
  PYTHON_PATH ${CMAKE_BINARY_DIR}/lib/site-packages
  DEPENDS coal_pywrap_nb
)
add_dependencies(coal_python coal_pywrap_nb)

xxx_python_compile_all(
  DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

install(
    DIRECTORY ${CMAKE_BINARY_DIR}/lib/site-packages/test_project_bp
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/site-packages
    FILES_MATCHING 
        PATTERN "*.py" 
        PATTERN "*.pyc" 
        PATTERN "*.typed" 
        PATTERN "*.so" 
        PATTERN "*.pyd"
)
