import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def audit_bank_port_collision():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS STAGE 1 AUDIT: BANK PORT CONFLICT AVOIDANCE (AX_05)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 构建冲突场景：Inst A (Lat 4) at T=0 -> Write at T=5
    # 若 Inst B (Lat 1) 想在 T=x Read，系统需找到不冲突的 T_a, T_b 和 II
    insts = [
        {"id": "A", "unit": "FPADD", "bank_id": 0},
        {"id": "B", "unit": "LOGIC", "bank_id": 0}
    ]
    # 无依赖，仅靠 Bank 端口约束进行调度
    deps = []
    
    print("[RUN] Compiling with potential Bank Port Conflict at Cycle 5...")
    result = compiler.compile_kernel(insts, deps)
    
    if result["status"] == "SUCCESS":
        compiler.print_timing_report(result)
        
        # 验证：B 是否避开了 T=5
        trace = result["logical_trace"]
        t_a = next(t for t, v in trace.items() if 'A' in str(v['units']))
        t_b = next(t for t, v in trace.items() if 'B' in str(v['units']))
        
        print(f"\n[AUDIT] A starts at {t_a}, B starts at {t_b}")
        # A 的写回在 t_a+5
        write_cycle = t_a + 5
        if t_b == write_cycle:
            print(f"❌ Fail: B started at {t_b}, which exactly collides with A's Write-back!")
        else:
            print(f"✅ Success: Solver avoided Cycle {write_cycle}. B shifted to {t_b}.")
            
    else:
        print(f"❌ Fail: Solver could not find a solution!")

if __name__ == "__main__":
    audit_bank_port_collision()
