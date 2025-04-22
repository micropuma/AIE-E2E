cmake_minimum_required(VERSION 3.12)

project(tpu-mlir LANGUAGES CXX C)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

# 包含 Python 配置
include(AddMLIRPython)
include(MLIRDetectPythonEnv)
mlir_configure_python_dev_packages()

# 设置 Python 模块的根目录和输出目录
set(TOP_MLIR_PYTHON_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tpu_mlir")
set(TOP_MLIR_PYTHON_PACKAGES_DIR "${CMAKE_BINARY_DIR}/python")

# MLIR/LLVM 配置
set(MLIR_BINARY_DIR ${CMAKE_INSTALL_PREFIX})
find_package(MLIR REQUIRED CONFIG)

# 包含必要的头文件
include_directories(${LLVM_INCLUDE_DIRS})
include_directories(${MLIR_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)

# 结构性分组
declare_mlir_python_sources(TPUMLIRPythonSources)
declare_mlir_python_sources(TPUMLIRPythonSources.Dialects
  ROOT_DIR "${TOP_MLIR_PYTHON_ROOT_DIR}"
  ADD_TO_PARENT TPUMLIRPythonSources
)

# 定义方言绑定
declare_mlir_dialect_python_bindings(
  ADD_TO_PARENT TPUMLIRPythonSources.Dialects
  ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tpu_mlir"
  TD_FILE dialects/TopOps.td
  SOURCES dialects/top.py
  DIALECT_NAME top)

declare_mlir_dialect_python_bindings(
  ADD_TO_PARENT TPUMLIRPythonSources.Dialects
  ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tpu_mlir"
  TD_FILE dialects/TpuOps.td
  SOURCES dialects/tpu.py
  DIALECT_NAME tpu)

# 注册 Python 扩展
declare_mlir_python_extension(TPUMLIRPythonExtension.RegisterEverything
  MODULE_NAME _mlirRegisterEverything
  ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tpu_mlir"
  SOURCES
    RegisterEverything.cpp
  EMBED_CAPI_LINK_LIBS
    TPUMLIRCAPI
)

# 公共 CAPI 依赖的共享库
add_mlir_python_common_capi_library(TPUMLIRPythonCAPI
  INSTALL_COMPONENT TPUMLIRPythonModules
  INSTALL_DESTINATION python/mlir/_mlir_libs
  OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/python/mlir/_mlir_libs"
  RELATIVE_INSTALL_ROOT "../../.."
  DECLARED_SOURCES
    TPUMLIRPythonSources
    TPUMLIRPythonExtension.RegisterEverything
    MLIRPythonSources.Core
  EMBED_LIBS
    MLIRCAPIQuant
)

# 组装模块
add_mlir_python_modules(TPUMLIRPythonModules
  ROOT_PREFIX "${CMAKE_BINARY_DIR}/python/mlir"
  INSTALL_PREFIX "python/mlir/"
  DECLARED_SOURCES
    TPUMLIRPythonSources
    MLIRPythonSources.Core
    MLIRPythonSources.Dialects.quant
    MLIRPythonSources.Dialects.tosa
    MLIRPythonSources.Dialects.func
    TPUMLIRPythonExtension.RegisterEverything
  COMMON_CAPI_LINK_LIBS
    TPUMLIRPythonCAPI
)

# 添加子目录
add_subdirectory(transform)
add_subdirectory(third_party)

# 安装 Python 文件
install(
  DIRECTORY ./ DESTINATION python FILES_MATCHING
  USE_SOURCE_PERMISSIONS
  PATTERN "*.py"
  PATTERN "*.js"
  PATTERN "*.html"
  PATTERN "xlsx_to_py.py" EXCLUDE
  PATTERN "test_*" EXCLUDE
  PATTERN "__pycache__" EXCLUDE
  PATTERN ".pytest_cache" EXCLUDE
  PATTERN "tpu_mlir" EXCLUDE
  PATTERN "tools/soc_infer" EXCLUDE
)

# 安装特定的测试文件
install(
  DIRECTORY ./ DESTINATION python FILES_MATCHING
  USE_SOURCE_PERMISSIONS
  PATTERN "test_onnx.py"
  PATTERN "test_tpulang.py"
)

install(CODE "
  execute_process(COMMAND find \"\${CMAKE_INSTALL_PREFIX}/python\" -type d -empty -delete)
")

#-------------------------------------------------------------------------------
# Generate version info from Git
execute_process(
  COMMAND git describe --tags --always
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  RESULT_VARIABLE GIT_EXEC_RESULT
  OUTPUT_VARIABLE GIT_SHORT_HASH)

if (GIT_SHORT_HASH)
  string(STRIP ${GIT_SHORT_HASH} GIT_SHORT_HASH)
  string(FIND ${GIT_SHORT_HASH} "v" v_index)
  string(FIND ${GIT_SHORT_HASH} "V" V_index)
  if(v_index GREATER_EQUAL 0 OR V_index GREATER_EQUAL 0)
    string(FIND ${GIT_SHORT_HASH} "-" dash_index)
    if (dash_index GREATER_EQUAL 0)
      # ex: v1.12-beta.0-xx-xxxx
      string(SUBSTRING ${GIT_SHORT_HASH} 0 ${dash_index} MAIN_VERSION)
      math(EXPR dash_index "${dash_index} + 1")
      string(SUBSTRING ${GIT_SHORT_HASH} ${dash_index} -1 PATCH_VERSION)
      set(GIT_SHORT_HASH "${MAIN_VERSION}.${PATCH_VERSION}")
    else()
      # ex: v1.12
      set(GIT_SHORT_HASH "${GIT_SHORT_HASH}")
    endif()
  else()
    # no tag, just commit ID
    set(GIT_SHORT_HASH "v1.0.0.dev-${GIT_SHORT_HASH}")
  endif()
else()
  set(GIT_SHORT_HASH "UNKNOWN.UNKNOWN")
  message(STATUS "Cannot get version from git info, using default: ${GIT_SHORT_HASH}")
endif()

string(TIMESTAMP BUILD_TIME "%Y%m%d")
set(MLIR_VERSION "${GIT_SHORT_HASH}-${BUILD_TIME}" CACHE STRING "tpu-mlir version" FORCE)
set(BUILD_TIME "${BUILD_TIME}" CACHE STRING "Build time" FORCE)
message(STATUS "tpu-mlir version: ${MLIR_VERSION}")
add_definitions(-DMLIR_VERSION="${MLIR_VERSION}")

#-------------------------------------------------------------------------------

