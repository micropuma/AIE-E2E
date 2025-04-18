import os

chip = 'bm1690'

#print_ori_fx_graph/dump_fx_graph/skip_tpu_compile/dump_bmodel_input
debug_cmd = os.environ.get("TORCH_TPU_DEBUG_CMD", "disable_dot,const_name")

only_compile_graph_id = int(os.environ.get("TORCH_TPU_ONLY_COMPILE_GRAPH_ID", -1))

num_core = int(os.environ.get("TORCH_TPU_CORE_NUM", 1))
if chip == 'bm1690':
    num_core = 8

compile_opt = int(os.environ.get("TORCH_TPU_MLIR_COMPILE_OPT", 2))

#fp_mode
#test_input
cmp = False

unit_test = False