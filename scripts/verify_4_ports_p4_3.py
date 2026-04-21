import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def verify_global_port_limit():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS STAGE 1 AUDIT: GLOBAL PORT CONCURRENCY (4-PORT LIMIT)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 模拟 8 条指令，分别使用 8 个不同的 Bank (0-7)
    # 局部无冲突，但全局 Read 端口有压力
    insts = [{"id": f"OP_{i}", "unit": "LOGIC", "bank_id": i} for i in range(8)]
    deps = []
    
    print(f"[RUN] Attempting to compile 8 parallel Ops with 4 global ports...")
    result = compiler.compile_kernel(insts, deps)
    
    if result["status"] == "SUCCESS":
        # 验证 II 是否为 2 (8 ops / 4 ports = 2)
        print(f"✅ Success: Optimal II found: {result['ii']}")
        if result["ii"] == 2:
            print("✅ Success: Global Port Limit of 4 correctly constrained 8 Ops into II=2.")
        else:
            print(f"⚠️ Note: Solver found II={result['ii']}. (Expected 2 for matching port quota)")
            
        # 打印时序，展示端口分布
        compiler.print_timing_report(result)
    else:
        print(f"❌ Fail: Solver failed to find a valid schedule.")

if __name__ == "__main__":
    verify_global_port_limit()
