import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def verify_20_sets_compilation():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P3.2 Verification Trace: 20-Set Data Compression (LOOPS=19)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 模拟：1 次 FPADD 动作，重复执行 20 次 (add(a[0-19]))
    insts = [
        {"id": "ADD_VEC", "unit": "FPADD", "params": {"loops": 19}}
    ]
    deps = []
    
    print("[STEP 1] Compiling 20-Set Vectorized Addition...")
    output = compiler.compile_kernel(insts, deps)
    
    if output["status"] == "SUCCESS":
        print(f"✅ Success: Compiled into {len(output['binary'])} instruction(s).")
        binary_entry = output['binary'][0]
        hex_data = binary_entry['hex']
        print(f"   Instruction Hex: {hex_data}")
        
        # 物理验证 LOOPS 字段位置 (V4.2 SDD: LOOPS 位于 MSB-22 到 MSB-29)
        # 换算到 128-bit: [105:98]
        full_int = int(hex_data, 16)
        # 在 Packer 实现中：loops << 11 (相对于 41-bit header)
        # header 位于位偏移 87 位置 [127-41+1 = 87]
        # 所以 loops 实际位于 87 + 11 = 98 位开始。
        loops_extracted = (full_int >> 98) & 0xFF
        
        if loops_extracted == 19:
            print(f"✅ Success: LOOPS field correctly verified as 19 (Binary 0x13).")
        else:
            print(f"❌ Fail: Expected LOOPS 19, but extracted {loops_extracted}.")
    else:
        print(f"❌ Fail: Compilation failed with {output.get('reason')}")

if __name__ == "__main__":
    verify_20_sets_compilation()
