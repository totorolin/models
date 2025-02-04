# Linux GPU/CPU 离线量化功能开发文档

# 目录

- [1. 简介](#1)
- [2. 离线量化功能开发](#2)
    - [2.1 准备校准数据和环境](#2.1)
    - [2.2 准备推理模型](#2.2)
    - [2.3 准备离线量化代码](#2.3)
    - [2.4 开始离线量化](#2.4)
    - [2.5 验证推理结果正确性](#2.5)
- [3. FAQ](#3)
    - [3.1 通用问题](#3.1)


<a name="1"></a>

## 1. 简介

Paddle中静态离线量化，使用少量校准数据计算量化因子，可以快速将FP32模型量化成低比特模型（比如最常用的int8量化）。使用该量化模型进行预测，可以减少计算量、降低计算内存、减小模型大小。

更多关于Paddle 模型离线量化的介绍，可以参考[Paddle 离线量化官网教程](https://github.com/PaddlePaddle/PaddleSlim/blob/develop/docs/zh_cn/api_cn/static/quant/quantization_api.rst#quant_post_static)。

<a name="2"></a>

## 2. 离线量化功能开发

Paddle 离线量化开发可以分为个步骤，如下图所示。

<div align="center">
    <img src="../images/post_infer_quant_guide.png" width="600">
</div>

其中设置了2个核验点，分别为：

* 准备推理模型
* 验证量化模型推理结果正确性

<a name="2.1"></a>

### 2.1 准备校准数据和环境

**【准备校准数据】**

由于离线量化需要获得网络预测的每层的scale值，用来做数值范围的映射，所以需要适量的数据执行网络前向，故需要事先准备好校准数据集。

以ImageNet1k数据集为例，可参考[数据准备文档](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6#32-%E5%87%86%E5%A4%87%E6%95%B0%E6%8D%AE)。

用于校准的数据最好选择训练集，数据量在500个样本左右即可。

**【准备开发环境】**

- 确定已安装PaddlePaddle最新版本，通过pip安装linux版本paddle命令如下，更多的版本安装方法可查看飞桨[官网](https://www.paddlepaddle.org.cn/)
- 确定已安装paddleslim最新版本，通过pip安装linux版本paddle命令如下，更多的版本安装方法可查看[PaddleSlim](https://github.com/PaddlePaddle/PaddleSlim)

```
pip install paddlepaddle-gpu
pip install paddleslim
```

<a name="2.2"></a>

### 2.2 准备推理模型

准备推理模型可参考[准备推理模型教程](https://github.com/PaddlePaddle/models/blob/release/2.3/tutorials/tipc/train_infer_python/infer_python.md#22-%E5%87%86%E5%A4%87%E6%8E%A8%E7%90%86%E6%A8%A1%E5%9E%8B)

最终会在`mv3_fp32_infer`文件夹下生成`model.pdmodel` 和 `model.pdiparams`两个预测模型文件。

<a name="2.3"></a>

### 2.3 开始离线量化

**【基本流程】**

基于PaddleSlim，使用接口``paddleslim.quant.quant_post_static``对模型进行离线量化：

- Step1：定义`sample_generator`，传入paddle.io.Dataloader实例化对象，用来遍历校准数据集

- Step2：开始离线量化


**【实战】**

1）定义DataLoader，数据集定义可以参考[Datasets定义](https://github.com/PaddlePaddle/models/blob/release/2.2/tutorials/mobilenetv3_prod/Step6/paddlevision/datasets/vision.py)

包装DataLoader，定义`sample_generator`：

```python
def sample_generator(loader):
    def __reader__():
        for indx, data in enumerate(loader):
            images = np.array(data[0])
            yield images

    return __reader__
```

2）开始离线量化

```python
from paddleslim.quant import quant_post_static
fp32_model_dir = 'mv3_fp32_infer'
quant_output_dir = 'quant_model'
use_gpu = True
place = paddle.CUDAPlace(0) if use_gpu else paddle.CPUPlace()
exe = paddle.static.Executor(place)
quant_post_static(
        executor=exe,
        model_dir=fp32_model_dir,
        quantize_model_path=quant_output_dir,
        sample_generator=sample_generator(data_loader),
        model_filename='model.pdmodel',
        params_filename='model.pdiparams',
        batch_size=32,
        batch_nums=10,
        algo='KL')
```

- 检查输出结果，确保离线量化后生成`__model__`和`__params__`文件。


**【实战】**

开始离线量化，具体可参考MobileNetv3[离线量化代码](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6/deploy/ptq_python/post_quant.py)。


<a name="2.5"></a>

### 2.5 通过Paddle Inference验证量化前模型和量化后模型的精度差异

**【基本流程】**

可参考[开发推理程序流程](https://github.com/PaddlePaddle/models/blob/release/2.3/tutorials/tipc/train_infer_python/infer_python.md#26-%E5%BC%80%E5%8F%91%E6%8E%A8%E7%90%86%E7%A8%8B%E5%BA%8F)

**【实战】**


1）初始化`paddle.inference`库并配置相应参数：

具体可以参考MobileNetv3 [Inference模型测试代码](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6/deploy/ptq_python/eval.py)

2）配置预测库输入输出：

具体可以参考MobileNetv3 [Inference模型测试代码](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6/deploy/ptq_python/eval.py)

3）开始预测：

具体可以参考MobileNetv3 [Inference模型测试代码](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6/deploy/ptq_python/eval.py)

4）测试单张图像预测结果是否正确，可参考[Inference预测文档](https://github.com/PaddlePaddle/models/blob/release/2.2/docs/tipc/train_infer_python/infer_python.md)

5）同时也可以测试量化模型和FP32模型的精度，确保量化后模型精度损失符合预期。参考[MobileNet量化模型精度验证文档](https://github.com/PaddlePaddle/models/tree/release/2.2/tutorials/mobilenetv3_prod/Step6/deploy/ptq_python/README.md)

<a name="3"></a>

## 3. FAQ

如果您在使用该文档完成离线量化的过程中遇到问题，可以给在[这里](https://github.com/PaddlePaddle/PaddleSlim/issues)提一个ISSUE，我们会高优跟进。

## 3.1 通用问题

- 如何选择离线量化方法？
选择合适的离线量化方法，比如`KL`、`hist`、`mse`等，具体离线量化方法选择可以参考API文档：[quant_post_static API文档](https://github.com/PaddlePaddle/PaddleSlim/blob/develop/docs/zh_cn/api_cn/static/quant/quantization_api.rst#quant_post_static)。
