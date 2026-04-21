import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def audit_stage_1_logic():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS STAGE 1 AUDIT: SMT SOLVER LOGICAL TIMING\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 算子：5 组数据的简单流水线 (ADD -> MUL)
    insts = [
        {"id": "A", "unit": "FPADD", "params": {"loops": 4}},
        {"id": "M", "unit": "FPMUL", "params": {"loops": 4}}
    ]
    deps = [("M", "A", 0)] # M 依赖于 A 产生的结果 (A 延迟 4)
    
    result = compiler.compile_kernel(insts, deps)
    
    if result["status"] == "SUCCESS":
        # 1. 输出逻辑报表
        compiler.print_timing_report(result)
        
        # 2. 机读审计 (Logical Auditor)
        trace = result["logical_trace"]
        
        # 验证点：ADD 发射时刻 T，其路由 PULSE 必须在 T+1
        t_add_start = 0 # 我们已知 ADD 从 0 开始
        if "rtovr_for_A" in trace[t_add_start + 1].get("rtovr", {}):
            print("✅ Logic Audit: RTOVR Pulse for ADD correctly synchronized at T+1.")
        else:
            print("❌ Logic Audit Fail: ADD RTOVR out of sync!")
            
        # 验证点：MUL 必须在 ADD 延迟 (4 周期) 后启动
        t_mul_start = next(t for t, v in result['logical_trace'].items() if 'FPMUL' in v['units'])
        print(f"\n[AUDIT] ADD_Start={t_add_start}, MUL_Start={t_mul_start}")
        if t_mul_start >= t_add_start + 4:
            print(f"✅ Logic Audit: Delay between ADD and MUL is {t_mul_start - t_add_start} (>= 4). PASS.")
        else:
            print("❌ Logic Audit Fail: MUL started before ADD latency finished!")
            
    else:
        print(f"❌ Fail: Compilation failed {result}")

if __name__ == "__main__":
    audit_stage_1_logic()
