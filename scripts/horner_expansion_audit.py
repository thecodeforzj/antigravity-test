import sys
import os
import json

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_compiler_main import SMTCompiler

def run_horner_6th_audit():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P4.4 FINAL AUDIT: 6th-Order Horner with Phase Filling (Decoupled R/W)\n")
    
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # 构造 6 阶霍纳 (12步计算)
    insts = []
    dependencies = []
    
    last_id = None
    for i in range(6, -1, -1):
        if i == 6:
            # 第一步：a6 * x (常数项读 Bank 7)
            m_id = f"MUL_{i}"
            insts.append({"id": m_id, "unit": "FPMUL", "read_bank": 7}) 
            last_id = m_id
        else:
            # ADD_i, MUL_i 循环
            a_id = f"ADD_{i}"
            # 只有最后一步 ADD_0 写回 Bank 7
            w_bank = 7 if i == 0 else None
            insts.append({"id": a_id, "unit": "FPADD", "read_bank": 7, "write_bank": w_bank})
            dependencies.append((a_id, last_id, 0))
            
            if i > 0:
                m_id = f"MUL_{i}"
                insts.append({"id": m_id, "unit": "FPMUL"}) 
                dependencies.append((m_id, a_id, 0))
                last_id = m_id
            else:
                last_id = a_id
                
    print(f"[RUN] Compiling Horner-6 (7 Reads, 1 Write to Bank 7)...")
    result = compiler.compile_kernel(insts, dependencies)
    
    if result["status"] == "SUCCESS":
        print(f"✅ Success: Horner-6 Scheduled with II = {result['ii']}")
        compiler.print_timing_report(result)
    else:
        print(f"❌ Fail: {result.get('reason')}")

if __name__ == "__main__":
    run_horner_6th_audit()
