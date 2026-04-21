import sys
import os
import json

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler
from app.smt_compiler_main import SMTCompiler

def verify_dsl_integration():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P4.5 UNIFIED COMPILER TEST: JSON DSL to SMT Schedule\n")
    
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    # 构造 Horner-6 JSON DSL
    dsl = []
    
    # 系数 a6...a0 
    # MUL_6 -> ADD_5 -> MUL_5 -> ADD_4 ... -> ADD_0
    
    prev_id = None
    for i in range(6, -1, -1):
        if i == 6:
            # MUL_i reads constant a_i (Bank 7)
            m_id = f"MUL_{i}"
            dsl.append({"id": m_id, "op": "FPMUL", "read_bank": 7})
            prev_id = m_id
        else:
            # ADD_i reads constant a_i (Bank 7)
            a_id = f"ADD_{i}"
            w_bank = 7 if i == 0 else None # Only last one writes
            dsl.append({"id": a_id, "op": "FPADD", "read_bank": 7, "write_bank": w_bank, "deps": [[prev_id, 0]]})
            
            if i > 0:
                m_id = f"MUL_{i}"
                dsl.append({"id": m_id, "op": "FPMUL", "deps": [[a_id, 0]]})
                prev_id = m_id
            else:
                prev_id = a_id
                
    print(f"[RUN] Compiling Horner-6 from dynamic JSON (Ops: {len(dsl)})")
    result = compiler.compile(dsl)
    
    if result["status"] == "SUCCESS":
        print(f"✅ Success: DSL Compiler achieved II = {result['ii']}")
        # Use SMTCompiler just for printing the report
        p_compiler = SMTCompiler(manifest_path)
        p_compiler.print_timing_report(result)
    else:
        print(f"❌ Fail: {result.get('reason')}")

if __name__ == "__main__":
    verify_dsl_integration()
