#pragma once

#include <cuda.h>
#include <cudnn.h>

#include "cinn/runtime/cinn_runtime.h"

namespace cinn {
namespace runtime {
namespace cuda {

const int kCUDAMaxCards{10};

/**
 * Call a CUDA compiled kernel.
 *
 * @param kernel_fn the compiled PTX kernel.
 * @param args an array of cinn_pod_value_ts(consists of scalars and buffers).
 */
void cinn_call_cuda_kernel(void* kernel_fn,
                           cinn_pod_value_t* args,
                           int num_args,
                           int grid_x,
                           int grid_y,
                           int grid_z,
                           int block_x,
                           int block_y,
                           int block_z,
                           void* stream);

void cinn_gpu_cudnn_conv2d(int input_n,
                           int input_c,
                           int input_h,
                           int input_w,
                           int weights_n,
                           int weights_c,
                           int weights_h,
                           int weights_w,
                           int pad_h,
                           int pad_w,
                           int stride_h,
                           int stride_w,
                           int dilation_h,
                           int dilation_w,
                           int output_n,
                           int output_c,
                           int output_h,
                           int output_w,
                           cinn_buffer_t* input,
                           cinn_buffer_t* weights,
                           cinn_buffer_t* output);
}  // namespace cuda
}  // namespace runtime
}  // namespace cinn
