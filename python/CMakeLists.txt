if(GENERATE_PYTHON_STUBS)
  include(${JRL_CMAKE_MODULES}/stubs.cmake)
endif()

# Name of the Python library
set(PYTHON_LIB_NAME ${PROJECT_NAME}_pywrap)

set(
  ${PYTHON_LIB_NAME}_HEADERS
  fwd.hh
  coal.hh
  deprecation.hh
  broadphase/fwd.hh
  broadphase/broadphase_collision_manager.hh
  broadphase/broadphase_callbacks.hh
  pickle.hh
  utils/std-pair.hh
  serializable.hh
)

set(
  ENABLE_PYTHON_DOXYGEN_AUTODOC
  TRUE
  CACHE BOOL
  "Enable automatic documentation of Python bindings from Doxygen documentation"
)

if(NOT ENABLE_PYTHON_DOXYGEN_AUTODOC OR NOT DOXYGEN_FOUND)
  set(ENABLE_DOXYGEN_AUTODOC FALSE)
else()
  set(ENABLE_DOXYGEN_AUTODOC TRUE)

  execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "import lxml"
    RESULT_VARIABLE _pypkg_found
    OUTPUT_QUIET
    ERROR_QUIET
  )
  if(_pypkg_found EQUAL 0)
    message(STATUS "Found Python package lxml.")
  else()
    set(ENABLE_DOXYGEN_AUTODOC FALSE)
    message(
      STATUS
      "Python package lxml not found. Python bindings will not be documented."
    )
    message(STATUS "  You can install it with: pip install lxml")
  endif()

  execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "import pylatexenc"
    RESULT_VARIABLE _pypkg_found
    OUTPUT_QUIET
    ERROR_QUIET
  )
  if(NOT _pypkg_found EQUAL 0)
    message(STATUS "Python package pylatexenc not found.")
    message(
      STATUS
      "  Formulas in the Python bindings documentation may look ugly."
    )
    message(STATUS "  You can install it with: pip install pylatexenc")
  endif()
  unset(_pypkg_found)
endif()
if(ENABLE_DOXYGEN_AUTODOC)
  add_custom_target(
    generate_doxygen_cpp_doc
    COMMAND
      ${PYTHON_EXECUTABLE}
      ${PROJECT_SOURCE_DIR}/doc/python/doxygen_xml_parser.py
      ${PROJECT_BINARY_DIR}/doc/doxygen-xml/index.xml
      ${CMAKE_CURRENT_BINARY_DIR}/doxygen_autodoc >
      ${CMAKE_CURRENT_BINARY_DIR}/doxygen_autodoc.log
    BYPRODUCTS
      ${CMAKE_CURRENT_BINARY_DIR}/doxygen_autodoc/doxygen_xml_parser_for_cmake.hh
      ${CMAKE_CURRENT_BINARY_DIR}/doxygen_autodoc.log
    COMMENT "Generating Doxygen C++ documentation"
  )
  add_dependencies(generate_doxygen_cpp_doc doc)

  list(
    APPEND
    ${PYTHON_LIB_NAME}_HEADERS
    ${CMAKE_CURRENT_BINARY_DIR}/doxygen_autodoc/doxygen_xml_parser_for_cmake.hh
  )
endif()

set(
  ${PYTHON_LIB_NAME}_SOURCES
  version.cc
  math.cc
  collision-geometries.cc
  collision.cc
  contact_patch.cc
  distance.cc
  coal.cc
  gjk.cc
  broadphase/broadphase.cc
)

if(COAL_HAS_OCTOMAP)
  list(APPEND ${PYTHON_LIB_NAME}_SOURCES octree.cc)
endif(COAL_HAS_OCTOMAP)

add_library(
  ${PYTHON_LIB_NAME}
  MODULE
  ${${PYTHON_LIB_NAME}_SOURCES}
  ${${PYTHON_LIB_NAME}_HEADERS}
)
target_include_directories(
  ${PYTHON_LIB_NAME}
  SYSTEM
  PRIVATE ${PYTHON_INCLUDE_DIRS}
)
target_include_directories(
  ${PYTHON_LIB_NAME}
  PRIVATE "${PROJECT_SOURCE_DIR}/src" "${CMAKE_CURRENT_BINARY_DIR}"
)
if(WIN32)
  target_link_libraries(${PYTHON_LIB_NAME} PUBLIC ${PYTHON_LIBRARY})
endif(WIN32)

add_dependencies(${PROJECT_NAME}_python ${PYTHON_LIB_NAME})
ADD_HEADER_GROUP(${PYTHON_LIB_NAME}_HEADERS)
ADD_SOURCE_GROUP(${PYTHON_LIB_NAME}_SOURCES)
if(ENABLE_DOXYGEN_AUTODOC)
  add_dependencies(${PYTHON_LIB_NAME} generate_doxygen_cpp_doc)
  target_compile_definitions(
    ${PYTHON_LIB_NAME}
    PRIVATE COAL_HAS_DOXYGEN_AUTODOC
  )
endif()

target_link_libraries(
  ${PYTHON_LIB_NAME}
  PUBLIC ${PROJECT_NAME}::${PROJECT_NAME} eigenpy::eigenpy Boost::boost
)

set_target_properties(
  ${PYTHON_LIB_NAME}
  PROPERTIES
    PREFIX ""
    SUFFIX "${PYTHON_EXT_SUFFIX}"
    OUTPUT_NAME "${PYTHON_LIB_NAME}"
    LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/python/${PROJECT_NAME}"
    # On Windows, shared library are treat as binary
    RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/python/${PROJECT_NAME}"
)

if(IS_ABSOLUTE ${PYTHON_SITELIB})
  set(ABSOLUTE_PYTHON_SITELIB ${PYTHON_SITELIB})
else()
  set(ABSOLUTE_PYTHON_SITELIB ${CMAKE_INSTALL_PREFIX}/${PYTHON_SITELIB})
endif()
set(${PYTHON_LIB_NAME}_INSTALL_DIR ${ABSOLUTE_PYTHON_SITELIB}/${PROJECT_NAME})
if(UNIX)
  GET_RELATIVE_RPATH(
    ${${PYTHON_LIB_NAME}_INSTALL_DIR}
    ${PYTHON_LIB_NAME}_INSTALL_RPATH
  )
  set_target_properties(
    ${PYTHON_LIB_NAME}
    PROPERTIES INSTALL_RPATH "${${PYTHON_LIB_NAME}_INSTALL_RPATH}"
  )
endif()

install(
  TARGETS ${PYTHON_LIB_NAME}
  EXPORT ${TARGETS_EXPORT_NAME}
  DESTINATION ${${PYTHON_LIB_NAME}_INSTALL_DIR}
)

# --- GENERATE STUBS
if(GENERATE_PYTHON_STUBS)
  LOAD_STUBGEN()
  GENERATE_STUBS(
    ${CMAKE_CURRENT_BINARY_DIR}
    ${PROJECT_NAME}
    ${ABSOLUTE_PYTHON_SITELIB}
    ${PYTHON_LIB_NAME}
    ${PROJECT_NAME}::${PROJECT_NAME}
  )
endif(GENERATE_PYTHON_STUBS)

# --- INSTALL SCRIPTS
set(PYTHON_FILES __init__.py viewer.py windows_dll_manager.py)

foreach(python ${PYTHON_FILES})
  PYTHON_BUILD(${PROJECT_NAME} ${python})
  install(
    FILES "${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}/${python}"
    DESTINATION ${${PYTHON_LIB_NAME}_INSTALL_DIR}
  )
endforeach(python)

if(COAL_BACKWARD_COMPATIBILITY_WITH_HPP_FCL)
  PYTHON_INSTALL_ON_SITE(hppfcl __init__.py COMPONENT hpp-fcl-compatibility)
  PYTHON_INSTALL_ON_SITE(hppfcl viewer.py COMPONENT hpp-fcl-compatibility)
endif()
