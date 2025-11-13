function(coal_python_add_test name)
  set(test_name "coal: Python ${name}")
  set(source "test_${name}.py")
  add_test(
    NAME ${test_name}
    COMMAND $<TARGET_FILE:Pytest::Pytest> ${CMAKE_CURRENT_SOURCE_DIR}/${source}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  )
  set_tests_properties(
    ${test_name}
    PROPERTIES
      ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}:${CMAKE_BINARY_DIR}/lib/site-packages"
      DEPENDS coal
  )
endfunction()

coal_python_add_test(api)
coal_python_add_test(test_case)
coal_python_add_test(test_collision_manager)
coal_python_add_test(test_collision)
coal_python_add_test(test_geometric_shapes)
coal_python_add_test(test_pickling)
