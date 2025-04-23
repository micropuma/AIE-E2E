#!/bin/bash

LLVM_PATH=$PWD/externals/llvm/build/

if [ -d "build" ]; then
    echo "删除旧build目录..."
    rm -rf build
fi

echo "创建新build目录..."
mkdir build && cd build

echo "开始CMake配置..."
cmake -G Ninja .. \
    -DLLVM_DIR="${LLVM_PATH}/lib/cmake/llvm" \
    -DMLIR_DIR="${LLVM_PATH}/lib/cmake/mlir"

echo "开始编译..."
ninja -j $(nproc)
