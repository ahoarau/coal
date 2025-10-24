#
# Copyright (c) 2022-2026 INRIA
#
cmake_minimum_required(VERSION 3.22...4.1)

include(FetchContent)
FetchContent_Declare(
  cmake-utils
  GIT_REPOSITORY https://github.com/ahoarau/cmake-utils.git
  GIT_TAG main
)
FetchContent_MakeAvailable(cmake-utils)

project(
  coal
  VERSION 3.0.2
  DESCRIPTION
    "Coal, The Collision Detection Library. Previously known as HPP-FCL, fork of FCL -- The Flexible Collision Library"
  HOMEPAGE_URL "https://github.com/coal-library/coal"
)
xxx_include_ctest()
include(CMakeDependentOption)
xxx_configure_default_build_type(Release)
xxx_configure_default_install_prefix(${CMAKE_CURRENT_BINARY_DIR}/tmp-install)
xxx_configure_default_binary_dirs()
xxx_configure_default_install_dirs()
xxx_configure_apple_rpath()

# ----------------------------------------------------
# --- OPTIONS  ---------------------------------------
# ----------------------------------------------------
xxx_option(COAL_INSTALL_DOCUMENTATION "Generate and install the documentation" OFF)
xxx_option(COAL_INSTALL_HEADERS "Install the header files" ON)
xxx_cmake_dependent_option(
  COAL_BUILD_DOCUMENTATION
  "Build the documentation"
  OFF
  COAL_INSTALL_DOCUMENTATION
  OFF
)

xxx_option(COAL_BUILD_TESTS "Build the tests" OFF)
xxx_option(SUFFIX_SO_VERSION "Suffix library name with its version" OFF)
xxx_option(
  COAL_TURN_ASSERT_INTO_EXCEPTION
  "Turn some critical Coal asserts to exception."
  OFF
)
xxx_option(
  COAL_BUILD_WITH_LOGGING
  "Activate logging for warnings or error messages. Turned on by default in Debug."
  OFF
)
xxx_option(
  COAL_BACKWARD_COMPATIBILITY_WITH_HPP_FCL
  "Make Coal retro-compatible with HPP-FCL."
  OFF
)
xxx_option(
  COAL_USE_FLOAT_PRECISION
  "Use float precision (32-bit) instead of the default double precision (64-bit)"
  OFF
)
xxx_option(
  COAL_BUILD_WITH_TRACY
  "Build with tracy profiler for performance analysis"
  OFF
)
xxx_option(
  COAL_BUILD_WITH_OCTOMAP
  "Build with Octomap support"
  OFF
)
xxx_option(
  COAL_BUILD_WITH_QHULL
  "Build with QHull support"
  OFF
)

xxx_cmake_dependent_option(
  COAL_PYTHON_NANOBIND
  "Build the nanobind-based bindings."
  OFF
  BUILD_PYTHON_INTERFACE
  OFF
)
if(NOT COAL_PYTHON_NANOBIND)
  xxx_cmake_dependent_option(
    GENERATE_PYTHON_STUBS
    "Generate the Python stubs for the Python bindings (only for legacy Boost.Python bindings)"
    OFF
    BUILD_PYTHON_INTERFACE
    OFF
  )
endif()

# ----------------------------------------------------
# --- Dependencies  ----------------------------------
# ----------------------------------------------------

xxx_find_package(Eigen3 3.4.0 CONFIG REQUIRED)

xxx_find_package(Boost CONFIG REQUIRED COMPONENTS serialization filesystem)

xxx_find_package(assimp CONFIG REQUIRED)

if(COAL_BUILD_WITH_LOGGING)
  xxx_find_package(Boost CONFIG REQUIRED COMPONENTS log)
endif()

if(COAL_BUILD_WITH_TRACY)
  xxx_find_package(Tracy CONFIG REQUIRED)
endif()


if(COAL_BUILD_WITH_OCTOMAP)
  xxx_find_package(octomap 1.8.0 CONFIG REQUIRED)
endif()

if(COAL_BUILD_WITH_QHULL)
  xxx_find_package(Qhull CONFIG REQUIRED COMPONENTS qhull_r qhullcpp)
endif()

if(COAL_BUILD_TESTS)
  xxx_find_package(Boost CONFIG REQUIRED COMPONENTS unit_test_framework)
endif()

if(BUILD_PYTHON_INTERFACE AND BUILD_STANDALONE_PYTHON_INTERFACE)
  xxx_find_package(coal CONFIG REQUIRED)
endif()

if(BUILD_PYTHON_INTERFACE AND COAL_PYTHON_NANOBIND)
  xxx_find_nanobind()
  xxx_find_package(nanoeigenpy CONFIG REQUIRED)
endif()

if(BUILD_PYTHON_INTERFACE AND NOT COAL_PYTHON_NANOBIND)
  xxx_find_package(eigenpy 2.9.2 CONFIG REQUIRED)
endif()

# ----------------------------------------------------

add_library(coal SHARED)
xxx_target_enforce_msvc_conformance(coal PRIVATE)
target_compile_features(coal PUBLIC cxx_std_17)

if(WIN32)
  # There is an issue with MSVC 2017 and Eigen (due to std::aligned_storage).
  # See https://github.com/ceres-solver/ceres-solver/issues/481
  target_compile_definitions(coal PRIVATE _ENABLE_EXTENDED_ALIGNED_STORAGE)
  target_compile_definitions(coal PUBLIC NOMINMAX)
endif()

target_compile_definitions(
  coal
  PUBLIC
    $<$<BOOL:${COAL_USE_FLOAT_PRECISION}>:COAL_USE_FLOAT_PRECISION>
    $<$<BOOL:${COAL_TURN_ASSERT_INTO_EXCEPTION}>:COAL_TURN_ASSERT_INTO_EXCEPTION>
    $<$<BOOL:${COAL_BACKWARD_COMPATIBILITY_WITH_HPP_FCL}>:COAL_BACKWARD_COMPATIBILITY_WITH_HPP_FCL>
    $<$<BOOL:${COAL_BUILD_WITH_OCTOMAP}>:COAL_HAS_OCTOMAP>
    $<$<BOOL:${COAL_BUILD_WITH_QHULL}>:COAL_HAS_QHULL>
    $<$<BOOL:${COAL_BUILD_WITH_TRACY}>:COAL_TRACY_ENABLE>
    $<$<BOOL:${COAL_BUILD_WITH_LOGGING}>:COAL_BUILD_WITH_LOGGING BOOST_LOG_DYN_LINK>
)
target_link_libraries(
  coal
  PUBLIC
    Eigen3::Eigen
    Boost::serialization Boost::filesystem
    assimp::assimp
    $<$<BOOL:${COAL_BUILD_WITH_LOGGING}>:Boost::log>
    $<$<BOOL:${COAL_BUILD_WITH_OCTOMAP}>:octomap>
    $<$<BOOL:${COAL_BUILD_WITH_QHULL}>:Qhull::qhull_r Qhull::qhullcpp>
    $<$<BOOL:${COAL_BUILD_WITH_TRACY}>:Tracy::TracyClient>
)

target_include_directories(
  coal
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
set_target_properties(coal PROPERTIES VERSION ${PROJECT_VERSION})
xxx_target_generate_config_header(coal PUBLIC FILENAME coal/config.hh)
xxx_target_generate_warning_header(coal PUBLIC FILENAME coal/warning.hh)
xxx_target_generate_deprecated_header(coal PUBLIC FILENAME coal/deprecated.hh)
xxx_target_generate_tracy_header(coal PUBLIC FILENAME coal/tracy.hh)

target_sources(
  coal
  PRIVATE
    src/collision.cpp
    src/contact_patch.cpp
    src/contact_patch/contact_patch_solver.cpp
    src/contact_patch_func_matrix.cpp
    src/distance_func_matrix.cpp
    src/collision_data.cpp
    src/collision_node.cpp
    src/collision_object.cpp
    src/BV/RSS.cpp
    src/BV/AABB.cpp
    src/BV/kIOS.cpp
    src/BV/kDOP.cpp
    src/BV/OBBRSS.cpp
    src/BV/OBB.cpp
    src/broadphase/default_broadphase_callbacks.cpp
    src/broadphase/broadphase_dynamic_AABB_tree.cpp
    src/broadphase/broadphase_dynamic_AABB_tree_array.cpp
    src/broadphase/broadphase_bruteforce.cpp
    src/broadphase/broadphase_collision_manager.cpp
    src/broadphase/broadphase_SaP.cpp
    src/broadphase/broadphase_SSaP.cpp
    src/broadphase/broadphase_interval_tree.cpp
    src/broadphase/detail/interval_tree.cpp
    src/broadphase/detail/interval_tree_node.cpp
    src/broadphase/detail/simple_interval.cpp
    src/broadphase/detail/spatial_hash.cpp
    src/broadphase/detail/morton.cpp
    src/narrowphase/gjk.cpp
    src/narrowphase/minkowski_difference.cpp
    src/narrowphase/support_functions.cpp
    src/narrowphase/details.h
    src/shape/geometric_shapes.cpp
    src/shape/geometric_shapes_utility.cpp
    src/distance/box_halfspace.cpp
    src/distance/box_plane.cpp
    src/distance/box_sphere.cpp
    src/distance/capsule_capsule.cpp
    src/distance/capsule_halfspace.cpp
    src/distance/capsule_plane.cpp
    src/distance/cone_halfspace.cpp
    src/distance/cone_plane.cpp
    src/distance/cylinder_halfspace.cpp
    src/distance/cylinder_plane.cpp
    src/distance/sphere_sphere.cpp
    src/distance/sphere_cylinder.cpp
    src/distance/sphere_halfspace.cpp
    src/distance/sphere_plane.cpp
    src/distance/sphere_capsule.cpp
    src/distance/ellipsoid_halfspace.cpp
    src/distance/ellipsoid_plane.cpp
    src/distance/convex_halfspace.cpp
    src/distance/convex_plane.cpp
    src/distance/triangle_halfspace.cpp
    src/distance/triangle_plane.cpp
    src/distance/triangle_triangle.cpp
    src/distance/triangle_sphere.cpp
    src/distance/halfspace_plane.cpp
    src/distance/plane_plane.cpp
    src/distance/halfspace_halfspace.cpp
    src/intersect.cpp
    src/math/transform.cpp
    src/traversal/traversal_recurse.cpp
    src/distance.cpp
    src/BVH/BVH_utility.cpp
    src/BVH/BV_fitter.cpp
    src/BVH/BVH_model.cpp
    src/BVH/BV_splitter.cpp
    src/collision_func_matrix.cpp
    src/collision_utility.cpp
    src/mesh_loader/assimp.cpp
    src/mesh_loader/loader.cpp
    src/hfield.cpp
    src/serialization/serialization.cpp
    $<$<BOOL:${COAL_BUILD_WITH_OCTOMAP}>:src/octree.cpp>
)

xxx_declare_component(TARGETS coal COMPONENT coal)
xxx_target_headers(coal PUBLIC
  HEADERS
    include/coal/collision_data.h
    include/coal/BV/kIOS.h
    include/coal/BV/BV.h
    include/coal/BV/RSS.h
    include/coal/BV/OBBRSS.h
    include/coal/BV/BV_node.h
    include/coal/BV/AABB.h
    include/coal/BV/OBB.h
    include/coal/BV/kDOP.h
    include/coal/broadphase/broadphase.h
    include/coal/broadphase/broadphase_SSaP.h
    include/coal/broadphase/broadphase_SaP.h
    include/coal/broadphase/broadphase_bruteforce.h
    include/coal/broadphase/broadphase_collision_manager.h
    include/coal/broadphase/broadphase_continuous_collision_manager-inl.h
    include/coal/broadphase/broadphase_continuous_collision_manager.h
    include/coal/broadphase/broadphase_dynamic_AABB_tree-inl.h
    include/coal/broadphase/broadphase_dynamic_AABB_tree.h
    include/coal/broadphase/broadphase_dynamic_AABB_tree_array-inl.h
    include/coal/broadphase/broadphase_dynamic_AABB_tree_array.h
    include/coal/broadphase/broadphase_interval_tree.h
    include/coal/broadphase/broadphase_spatialhash-inl.h
    include/coal/broadphase/broadphase_spatialhash.h
    include/coal/broadphase/broadphase_callbacks.h
    include/coal/broadphase/default_broadphase_callbacks.h
    include/coal/broadphase/detail/hierarchy_tree-inl.h
    include/coal/broadphase/detail/hierarchy_tree.h
    include/coal/broadphase/detail/hierarchy_tree_array-inl.h
    include/coal/broadphase/detail/hierarchy_tree_array.h
    include/coal/broadphase/detail/interval_tree.h
    include/coal/broadphase/detail/interval_tree_node.h
    include/coal/broadphase/detail/morton-inl.h
    include/coal/broadphase/detail/morton.h
    include/coal/broadphase/detail/node_base-inl.h
    include/coal/broadphase/detail/node_base.h
    include/coal/broadphase/detail/node_base_array-inl.h
    include/coal/broadphase/detail/node_base_array.h
    include/coal/broadphase/detail/simple_hash_table-inl.h
    include/coal/broadphase/detail/simple_hash_table.h
    include/coal/broadphase/detail/simple_interval-inl.h
    include/coal/broadphase/detail/simple_interval.h
    include/coal/broadphase/detail/sparse_hash_table-inl.h
    include/coal/broadphase/detail/sparse_hash_table.h
    include/coal/broadphase/detail/spatial_hash-inl.h
    include/coal/broadphase/detail/spatial_hash.h
    include/coal/narrowphase/narrowphase.h
    include/coal/narrowphase/gjk.h
    include/coal/narrowphase/narrowphase_defaults.h
    include/coal/narrowphase/minkowski_difference.h
    include/coal/narrowphase/support_data.h
    include/coal/narrowphase/support_functions.h
    include/coal/shape/convex.h
    include/coal/shape/convex.hxx
    include/coal/shape/geometric_shape_to_BVH_model.h
    include/coal/shape/geometric_shapes.h
    include/coal/shape/geometric_shapes.hxx
    include/coal/shape/geometric_shapes_traits.h
    include/coal/shape/geometric_shapes_utility.h
    include/coal/distance_func_matrix.h
    include/coal/collision.h
    include/coal/collision_func_matrix.h
    include/coal/contact_patch.h
    include/coal/contact_patch_func_matrix.h
    include/coal/contact_patch/contact_patch_solver.h
    include/coal/contact_patch/contact_patch_solver.hxx
    include/coal/distance.h
    include/coal/math/matrix_3f.h
    include/coal/math/vec_3f.h
    include/coal/math/types.h
    include/coal/math/transform.h
    include/coal/data_types.h
    include/coal/BVH/BVH_internal.h
    include/coal/BVH/BVH_model.h
    include/coal/BVH/BVH_front.h
    include/coal/BVH/BVH_utility.h
    include/coal/collision_object.h
    include/coal/collision_utility.h
    include/coal/hfield.h
    include/coal/fwd.hh
    include/coal/logging.h
    include/coal/mesh_loader/assimp.h
    include/coal/mesh_loader/loader.h
    include/coal/internal/BV_fitter.h
    include/coal/internal/BV_splitter.h
    include/coal/internal/shape_shape_func.h
    include/coal/internal/shape_shape_contact_patch_func.h
    include/coal/internal/intersect.h
    include/coal/internal/intersect.hxx
    include/coal/internal/tools.h
    include/coal/internal/traversal_node_base.h
    include/coal/internal/traversal_node_bvh_shape.h
    include/coal/internal/traversal_node_bvhs.h
    include/coal/internal/traversal_node_hfield_shape.h
    include/coal/internal/traversal_node_setup.h
    include/coal/internal/traversal_node_shapes.h
    include/coal/internal/traversal_recurse.h
    include/coal/internal/traversal.h
    include/coal/serialization/fwd.h
    include/coal/serialization/serializer.h
    include/coal/serialization/archive.h
    include/coal/serialization/transform.h
    include/coal/serialization/AABB.h
    include/coal/serialization/BV_node.h
    include/coal/serialization/BV_splitter.h
    include/coal/serialization/BVH_model.h
    include/coal/serialization/collision_data.h
    include/coal/serialization/contact_patch.h
    include/coal/serialization/collision_object.h
    include/coal/serialization/convex.h
    include/coal/serialization/eigen.h
    include/coal/serialization/geometric_shapes.h
    include/coal/serialization/memory.h
    include/coal/serialization/OBB.h
    include/coal/serialization/RSS.h
    include/coal/serialization/OBBRSS.h
    include/coal/serialization/kIOS.h
    include/coal/serialization/kDOP.h
    include/coal/serialization/hfield.h
    include/coal/serialization/quadrilateral.h
    include/coal/serialization/triangle.h
    include/coal/timings.h
  BASE_DIRS include
)

if(COAL_BUILD_WITH_OCTOMAP)
  xxx_target_headers(coal PUBLIC
    HEADERS
      include/coal/octree.h
      include/coal/serialization/octree.h
      include/coal/internal/traversal_node_octree.h
    BASE_DIRS include
  )
endif()


add_library(coal-hpp-fcl-compatibility INTERFACE)
target_link_libraries(coal-hpp-fcl-compatibility INTERFACE coal)
target_include_directories(
  coal-hpp-fcl-compatibility
  INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
xxx_declare_component(TARGETS coal-hpp-fcl-compatibility COMPONENT coal-hpp-fcl-compatibility)
xxx_target_headers(coal-hpp-fcl-compatibility PUBLIC
  HEADERS
    include/hpp/fcl/broadphase/broadphase_bruteforce.h
    include/hpp/fcl/broadphase/broadphase_callbacks.h
    include/hpp/fcl/broadphase/broadphase_collision_manager.h
    include/hpp/fcl/broadphase/broadphase_continuous_collision_manager.h
    include/hpp/fcl/broadphase/broadphase_continuous_collision_manager-inl.h
    include/hpp/fcl/broadphase/broadphase_dynamic_AABB_tree_array.h
    include/hpp/fcl/broadphase/broadphase_dynamic_AABB_tree_array-inl.h
    include/hpp/fcl/broadphase/broadphase_dynamic_AABB_tree.h
    include/hpp/fcl/broadphase/broadphase_dynamic_AABB_tree-inl.h
    include/hpp/fcl/broadphase/broadphase.h
    include/hpp/fcl/broadphase/broadphase_interval_tree.h
    include/hpp/fcl/broadphase/broadphase_SaP.h
    include/hpp/fcl/broadphase/broadphase_spatialhash.h
    include/hpp/fcl/broadphase/broadphase_spatialhash-inl.h
    include/hpp/fcl/broadphase/broadphase_SSaP.h
    include/hpp/fcl/broadphase/default_broadphase_callbacks.h
    include/hpp/fcl/broadphase/detail/hierarchy_tree_array.h
    include/hpp/fcl/broadphase/detail/hierarchy_tree_array-inl.h
    include/hpp/fcl/broadphase/detail/hierarchy_tree.h
    include/hpp/fcl/broadphase/detail/hierarchy_tree-inl.h
    include/hpp/fcl/broadphase/detail/interval_tree.h
    include/hpp/fcl/broadphase/detail/interval_tree_node.h
    include/hpp/fcl/broadphase/detail/morton.h
    include/hpp/fcl/broadphase/detail/morton-inl.h
    include/hpp/fcl/broadphase/detail/node_base_array.h
    include/hpp/fcl/broadphase/detail/node_base_array-inl.h
    include/hpp/fcl/broadphase/detail/node_base.h
    include/hpp/fcl/broadphase/detail/node_base-inl.h
    include/hpp/fcl/broadphase/detail/simple_hash_table.h
    include/hpp/fcl/broadphase/detail/simple_hash_table-inl.h
    include/hpp/fcl/broadphase/detail/simple_interval.h
    include/hpp/fcl/broadphase/detail/simple_interval-inl.h
    include/hpp/fcl/broadphase/detail/sparse_hash_table.h
    include/hpp/fcl/broadphase/detail/sparse_hash_table-inl.h
    include/hpp/fcl/broadphase/detail/spatial_hash.h
    include/hpp/fcl/broadphase/detail/spatial_hash-inl.h
    include/hpp/fcl/BV/AABB.h
    include/hpp/fcl/BV/BV.h
    include/hpp/fcl/BV/BV_node.h
    include/hpp/fcl/BVH/BVH_front.h
    include/hpp/fcl/BVH/BVH_internal.h
    include/hpp/fcl/BVH/BVH_model.h
    include/hpp/fcl/BVH/BVH_utility.h
    include/hpp/fcl/BV/kDOP.h
    include/hpp/fcl/BV/kIOS.h
    include/hpp/fcl/BV/OBB.h
    include/hpp/fcl/BV/OBBRSS.h
    include/hpp/fcl/BV/RSS.h
    include/hpp/fcl/coal.hpp
    include/hpp/fcl/collision_data.h
    include/hpp/fcl/collision_func_matrix.h
    include/hpp/fcl/collision.h
    include/hpp/fcl/collision_object.h
    include/hpp/fcl/collision_utility.h
    include/hpp/fcl/config.hh
    include/hpp/fcl/contact_patch/contact_patch_solver.h
    include/hpp/fcl/contact_patch/contact_patch_solver.hxx
    include/hpp/fcl/contact_patch_func_matrix.h
    include/hpp/fcl/contact_patch.h
    include/hpp/fcl/data_types.h
    include/hpp/fcl/deprecated.hh
    include/hpp/fcl/distance_func_matrix.h
    include/hpp/fcl/distance.h
    include/hpp/fcl/fwd.hh
    include/hpp/fcl/hfield.h
    include/hpp/fcl/internal/BV_fitter.h
    include/hpp/fcl/internal/BV_splitter.h
    include/hpp/fcl/internal/intersect.h
    include/hpp/fcl/internal/shape_shape_contact_patch_func.h
    include/hpp/fcl/internal/shape_shape_func.h
    include/hpp/fcl/internal/tools.h
    include/hpp/fcl/internal/traversal.h
    include/hpp/fcl/internal/traversal_node_base.h
    include/hpp/fcl/internal/traversal_node_bvhs.h
    include/hpp/fcl/internal/traversal_node_bvh_shape.h
    include/hpp/fcl/internal/traversal_node_hfield_shape.h
    include/hpp/fcl/internal/traversal_node_setup.h
    include/hpp/fcl/internal/traversal_node_shapes.h
    include/hpp/fcl/internal/traversal_recurse.h
    include/hpp/fcl/logging.h
    include/hpp/fcl/math/matrix_3f.h
    include/hpp/fcl/math/transform.h
    include/hpp/fcl/math/types.h
    include/hpp/fcl/math/vec_3f.h
    include/hpp/fcl/mesh_loader/assimp.h
    include/hpp/fcl/mesh_loader/loader.h
    include/hpp/fcl/narrowphase/gjk.h
    include/hpp/fcl/narrowphase/minkowski_difference.h
    include/hpp/fcl/narrowphase/narrowphase_defaults.h
    include/hpp/fcl/narrowphase/narrowphase.h
    include/hpp/fcl/narrowphase/support_data.h
    include/hpp/fcl/narrowphase/support_functions.h
    include/hpp/fcl/narrowphase/support_functions.hxx
    include/hpp/fcl/serialization/AABB.h
    include/hpp/fcl/serialization/archive.h
    include/hpp/fcl/serialization/BVH_model.h
    include/hpp/fcl/serialization/BV_node.h
    include/hpp/fcl/serialization/BV_splitter.h
    include/hpp/fcl/serialization/collision_data.h
    include/hpp/fcl/serialization/collision_object.h
    include/hpp/fcl/serialization/contact_patch.h
    include/hpp/fcl/serialization/convex.h
    include/hpp/fcl/serialization/eigen.h
    include/hpp/fcl/serialization/fwd.h
    include/hpp/fcl/serialization/geometric_shapes.h
    include/hpp/fcl/serialization/hfield.h
    include/hpp/fcl/serialization/kDOP.h
    include/hpp/fcl/serialization/kIOS.h
    include/hpp/fcl/serialization/memory.h
    include/hpp/fcl/serialization/OBB.h
    include/hpp/fcl/serialization/OBBRSS.h
    include/hpp/fcl/serialization/quadrilateral.h
    include/hpp/fcl/serialization/RSS.h
    include/hpp/fcl/serialization/serializer.h
    include/hpp/fcl/serialization/transform.h
    include/hpp/fcl/serialization/triangle.h
    include/hpp/fcl/shape/convex.h
    include/hpp/fcl/shape/convex.hxx
    include/hpp/fcl/shape/geometric_shapes.h
    include/hpp/fcl/shape/geometric_shapes.hxx
    include/hpp/fcl/shape/geometric_shapes_traits.h
    include/hpp/fcl/shape/geometric_shapes_utility.h
    include/hpp/fcl/shape/geometric_shape_to_BVH_model.h
    include/hpp/fcl/timings.h
    include/hpp/fcl/warning.hh
  BASE_DIRS include
)

if(COAL_BUILD_WITH_OCTOMAP)
  xxx_target_headers(coal-hpp-fcl-compatibility PUBLIC
    HEADERS
      include/hpp/fcl/octree.h
      include/hpp/fcl/serialization/octree.h
      include/hpp/fcl/internal/traversal_node_octree.h
    BASE_DIRS include
  )
endif()

if(COAL_INSTALL_HEADERS)
  xxx_install_headers()
endif()

xxx_generate_package_module_files()

if(COAL_BUILD_DOCUMENTATION)
  add_subdirectory(doc)
endif()

if(COAL_BUILD_TESTS)
  enable_testing()
  add_subdirectory(test)
endif()

if(BUILD_PYTHON_INTERFACE)
  add_custom_target(coal_python)
  set_target_properties(
    coal_python
    PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD True
  )
endif()

if(BUILD_PYTHON_INTERFACE AND COAL_PYTHON_NANOBIND)
  add_subdirectory(python-nb)
endif()

if(BUILD_PYTHON_INTERFACE AND NOT COAL_PYTHON_NANOBIND)
  add_subdirectory(python)
endif()

xxx_print_dependency_summary()
xxx_print_option_summary()