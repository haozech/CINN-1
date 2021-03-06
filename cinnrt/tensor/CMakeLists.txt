set(srcs
  tensor_map.cc
  tensor_shape.cc
  tensor_metadata.cc
  dense_host_tensor.cc
  dense_tensor_view.cc
  )

foreach(cpp ${srcs})
  set(core_src
    "${core_src};cinnrt/tensor/${cpp}"
    CACHE INTERNAL "")
endforeach()

file(GLOB includes LIST_DIRECTORIES false RELATIVE ${CMAKE_SOURCE_DIR} *.h)

foreach(header ${includes})
  set(core_includes "${core_includes};${header}" CACHE INTERNAL "")
endforeach()

set(tensor_map_mlir "${CMAKE_SOURCE_DIR}/cinnrt/dialect/mlir_tests/tensor_map.mlir")
set(external_kernels_lib "${CMAKE_BINARY_DIR}/paddle/libexternal_kernels.so")
message(STATUS "tensor_map_mlir: ${tensor_map_mlir}")
message(STATUS "external_kernels_lib: ${external_kernels_lib}")
add_test(
    NAME run_and_check_tensor_map
    COMMAND sh -c "${CMAKE_BINARY_DIR}/cinnrt/host_context/cinn-exec -i ${tensor_map_mlir} --shared_libs=${external_kernels_lib} | FileCheck-10 ${tensor_map_mlir}"
)
