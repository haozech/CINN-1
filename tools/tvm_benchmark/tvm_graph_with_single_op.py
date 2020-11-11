import os

import numpy as np

import tvm
from tvm import te
from tvm import autotvm
from tvm import relay
import tvm.relay.testing
from tvm.autotvm.tuner import XGBTuner, GATuner, RandomTuner, GridSearchTuner
from tvm.contrib.utils import tempdir
import tvm.contrib.graph_runtime as runtime

# To test different ops, change this single-op network.
# See ./relay_op.rst to get the op list.


def get_network_conv2d():
    input_shape = [(1, 512, 7, 7), (512, 512, 3, 3)]
    output_shape = (1, 512, 7, 7)
    input_names = ["x", "y"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    y = relay.Var(input_names[1], tvm.relay.TensorType(input_shape[1]))
    print("[Test]Begin building graph with op relay.nn.conv2d")
    mod = relay.Function([x, y],
                         relay.nn.conv2d(
                             x,
                             y,
                             kernel_size=(3, 3),
                             padding=(1, 1),
                             strides=(1, 1)))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_relu():
    input_shape = [(1, 512, 7, 7)]
    output_shape = (1, 512, 7, 7)
    input_names = ["x"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    print("[Test]Begin building graph with op relay.nn.relu")
    mod = relay.Function([x], relay.nn.relu(x))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_elementwise():
    input_shape = [(1, 512, 7, 7), (1, 512, 7, 7)]
    output_shape = (1, 512, 7, 7)
    input_names = ["x", "y"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    y = relay.Var(input_names[1], tvm.relay.TensorType(input_shape[1]))
    print("[Test]Begin building graph with op relay.multiply")
    mod = relay.Function([x, y], relay.multiply(x, y))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_matmul():
    input_shape = [(512, 512), (512, 512)]
    output_shape = (512, 512)
    input_names = ["x", "y"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    y = relay.Var(input_names[1], tvm.relay.TensorType(input_shape[1]))
    print("[Test]Begin building graph with op relay.nn.dense (matmul)")
    mod = relay.Function([x, y], relay.nn.dense(x, y))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_softmax():
    input_shape = [(1024, 2048)]
    output_shape = (1024, 2048)
    input_names = ["x"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    print("[Test]Begin building graph with op relay.nn.softmax")
    mod = relay.Function([x], relay.nn.softmax(x))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_pool2d():
    input_shape = [(1, 64, 112, 112)]
    output_shape = (1, 64, 56, 56)
    input_names = ["x"]
    x = relay.Var(input_names[0], tvm.relay.TensorType(input_shape[0]))
    print("[Test]Begin building graph with op relay.nn.max_pool2d")
    mod = relay.Function([x],
                         relay.nn.max_pool2d(
                             x,
                             pool_size=(3, 3),
                             strides=(2, 2),
                             padding=(1, 1)))
    params = []
    return mod, params, input_shape, output_shape, input_names


def get_network_batchnorm():
    data0 = relay.var("data0", relay.TensorType((1, 512, 7, 7), "float32"))
    bn_gamma = relay.var("bn_gamma1", relay.TensorType((512, ), "float32"))
    bn_beta = relay.var("bn_beta1", relay.TensorType((512, ), "float32"))
    bn_mmean = relay.var("bn_mean1", relay.TensorType((512, ), "float32"))
    bn_mvar = relay.var("bn_var1", relay.TensorType((512, ), "float32"))
    bn = relay.nn.batch_norm(data0, bn_gamma, bn_beta, bn_mmean, bn_mvar)[0]
    input_shape = [(1, 512, 7, 7), (512), (512), (512), (512)]
    output_shape = (1, 512, 7, 7)
    input_names = ["data0", "bn_gamma1", "bn_beta1", "bn_mean1", "bn_var1"]
    print("[Test]Begin building graph with op relay.nn.batch_norm")
    mod = relay.Function([data0, bn_gamma, bn_beta, bn_mmean, bn_mvar], bn)
    params = []
    return mod, params, input_shape, output_shape, input_names


#### DEVICE CONFIG ####
target = tvm.target.cuda()
dtype = "float32"


def tune_and_evaluate(func):
    # extract workloads from relay program
    mod, params, input_shape, out_shape, input_names = func()

    lib = relay.build_module.build(mod, target=target, params=params)

    # load parameters
    ctx = tvm.context(str(target), 0)
    module = runtime.GraphModule(lib["default"](ctx))
    for index in range(len(input_shape)):
        data_temp = tvm.nd.array(
            (np.random.uniform(size=input_shape[index])).astype(dtype))
        module.set_input(input_names[index], data_temp)
    # evaluate

    evaluator_preheat = module.module.time_evaluator(
        "run", ctx, number=50, repeat=50)
    evaluator = module.module.time_evaluator(
        "run", ctx, number=500, repeat=100)

    prof_res1 = np.array(
        evaluator_preheat().results) * 1000  # convert to millisecond
    print("[PreHeat]Mean inference time (std dev): %.4f ms (%.4f ms)" %
          (np.mean(prof_res1), np.std(prof_res1)))

    prof_res2 = np.array(evaluator().results) * 1000  # convert to millisecond
    print("[Benchmark]Mean inference time (std dev): %.4f ms (%.4f ms)" %
          (np.mean(prof_res2), np.std(prof_res2)))


tune_and_evaluate(get_network_conv2d)
tune_and_evaluate(get_network_pool2d)
tune_and_evaluate(get_network_softmax)
tune_and_evaluate(get_network_matmul)
tune_and_evaluate(get_network_batchnorm)
tune_and_evaluate(get_network_relu)
tune_and_evaluate(get_network_elementwise)