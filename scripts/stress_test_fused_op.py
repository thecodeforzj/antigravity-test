import sys
import os
import json

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def run_fused_op_stress_test():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P4 STRESS TEST: Fused Vector Pipeline (100 Sets)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 定义 100 组数据的融合算子
    # ADD 指令 (loops=99)
    # MUL 指令 (loops=99)
    insts = [
        {"id": "VEC_ADD", "unit": "FPADD", "params": {"loops": 99, "inc": 1}},
        {"id": "VEC_MUL", "unit": "FPMUL", "params": {"loops": 99, "inc": 1}}
    ]
    
    # 依赖：MUL 的输入依赖于 ADD 的输出，且额外增加 Bank 访问延迟
    dependencies = [
        ("VEC_MUL", "VEC_ADD", 0) # Base latency will be handled by solver (4 cycles)
    ]
    
    print("[RUN] Compiling 100-Set Fused Operation...")
    output = compiler.compile_kernel(insts, dependencies)
    
    if output["status"] == "SUCCESS":
        print(f"✅ Success: Pipeline generated with II = {output['ii']}")
        print(f"✅ Instructions: {len(output['binary'])} (Target: < 5 for high compression)")
        
        for entry in output['binary']:
            print(f"   T={entry['t']}: {entry['id'] if 'id' in entry else entry['ids']} -> Hex: {entry['hex']}")
            
        # 物理验证时序性
        t_add = next(e['t'] for e in output['binary'] if 'VEC_ADD' in e.get('ids', [e.get('id')]))
        t_mul = next(e['t'] for e in output['binary'] if 'VEC_MUL' in e.get('ids', [e.get('id')]))
        
        print(f"\n[AUDIT] Timing Gap: {t_mul - t_add} cycles.")
        if t_mul - t_add >= 4:
            print("✅ Success: Pipeline respect FPMUL/FPADD latency (4 cycles).")
        else:
            print("❌ Fail: Pipeline collision detected!")
    else:
        print(f"❌ Fail: Compilation failed with {output.get('reason')}")

if __name__ == "__main__":
    run_fused_op_stress_test()
