
import ctypes
import sys

import llvmlite.binding as llvm
from CodeGenerator import Block, GenerateCode, prTr

from Parser import build_tree, getTable


def run(llvm_ir):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()

    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = 1
    pm = llvm.create_module_pass_manager()
    pmb.populate(pm)
    pm.run(mod)

    engine = llvm.create_mcjit_compiler(mod, target_machine)
    init_ptr = engine.get_function_address('__init')
    init_func = ctypes.CFUNCTYPE(None)(init_ptr)
    init_func()
    main_ptr = engine.get_function_address('main')
    main_func = ctypes.CFUNCTYPE(None)(main_ptr)
    main_func()


def main():
    from llvmGen import compile_llvm

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m run Tests/filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()

    tree = build_tree(source)
    print("\n---------------------PARSING TREE---------------------")
    print(tree)
    print("\n---------------------TABLE OF SYMBOLS---------------------")
    print(getTable(tree))

    bloc = Block()
    bloc.inithead('Main')
    bloc = GenerateCode(bloc, tree, 'global', False , getTable(tree))
    print("\n---------------------TREE-ADDRESS CODE---------------------")
    prTr(bloc, 1)
    llvm_code = compile_llvm(bloc)
    with open('Code.ll', 'wb') as f:
        f.write(llvm_code.encode('utf-8'))
        f.flush()
    print("\n---------------------LLVM CODE---------------------")
    print(llvm_code)
    print("\n---------------------RUNNING THE PROGRAMM--------------------")
    run(llvm_code)

if __name__ == '__main__':
    main()
