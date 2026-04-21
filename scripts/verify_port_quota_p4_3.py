import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def verify_port_quota_logic():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS STAGE 1 AUDIT: OPERAND PORT QUOTA (3+2 Conflict)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 模拟两条指令：LOGIC(3 ports) + FPMUL(2 ports)
    # 它们加起来需要 5 个读取端口，硬件只有 4 个
    insts = [
        {"id": "A_LOGIC", "unit": "LOGIC"},
        {"id": "B_FPMUL", "unit": "FPMUL"}
    ]
    deps = []
    
    print("[RUN] Attempting to parallelize 5 operands on 4 ports...")
    result = compiler.compile_kernel(insts, deps)
    
    if result["status"] == "SUCCESS":
        compiler.print_timing_report(result)
        
        # 验证 T_a 和 T_b 是否错开
        trace = result["logical_trace"]
        t_a = next(t for t, v in trace.items() if 'A_LOGIC' in str(v['units']))
        t_b = next(t for t, v in trace.items() if 'B_FPMUL' in str(v['units']))
        
        print(f"\n[AUDIT] A starts at {t_a}, B starts at {t_b}")
        if t_a == t_b:
            print(f"❌ Fail: A and B both started at {t_a}, using {3+2}=5 ports total!")
        else:
            print(f"✅ Success: Solver correctly separated A and B to respect the 4-port limit.")
    else:
        print(f"❌ Fail: Solver failed {result}")

if __name__ == "__main__":
    verify_port_quota_logic()
