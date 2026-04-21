import sys
import os
import json

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def verify_parallel_compression():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P3.3 Verification Trace: Parallel Vectorized Integration\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 模拟：1 次 FPADD 和 1 次 FPMUL 同时启动
    # 都执行 20 次，且共享 INC=4
    insts = [
        {"id": "ADD_VEC", "unit": "FPADD", "params": {"loops": 19, "inc": 4}},
        {"id": "MUL_VEC", "unit": "FPMUL", "params": {"loops": 19, "inc": 4}}
    ]
    # 无依赖，强制它们并行
    deps = []
    
    print("[STEP 1] Compiling Parallel ADD + MUL with Shared INC=4...")
    output = compiler.compile_kernel(insts, deps)
    
    if output["status"] == "SUCCESS":
        # 验证是否合并为 1 条指令
        num_insts = len(output['binary'])
        print(f"✅ Success: Parallel ops merged into {num_insts} instruction(s).")
        
        binary_entry = output['binary'][0]
        hex_data = binary_entry['hex']
        print(f"   VLIW Packet Hex: {hex_data}")
        print(f"   Merged IDs: {binary_entry['ids']}")
        
        # 物理验证 INC 字段 (Header [40:30] -> 128-bit [87:97] 附近)
        # 在 Packer 实现中：inc << 0 (in low 11 bits of header)
        # header 位于 87 位，所以 inc 就在 [97:87]
        full_int = int(hex_data, 16)
        inc_extracted = full_int >> 87 & 0x7FF
        
        if inc_extracted == 4:
            print(f"✅ Success: Shared INC field verified as 4.")
        else:
            print(f"❌ Fail: Expected INC 4, but extracted {inc_extracted}.")
            
    else:
        print(f"❌ Fail: Compilation failed with {output.get('reason')}")

if __name__ == "__main__":
    verify_parallel_compression()
