import json
import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler

def run_bank0_anchor_test():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS V5.6 BANK-0 ANCHOR: Constants in Bank 0, Result in Bank 7\n")
    
    # 常数全部锁定在 Bank 0 (4 次访存)
    # 结果回写锁定在 Bank 7 (避开发生冲突)
    dsl = [
        {"id": "MUL_3", "op": "FPMUL", "read_bank": 0},
        {"id": "ADD_2", "op": "FPADD", "read_bank": 0, "deps": [["MUL_3", 0]]},
        {"id": "MUL_2", "op": "FPMUL", "deps": [["ADD_2", 0]]},
        {"id": "ADD_1", "op": "FPADD", "read_bank": 0, "deps": [["MUL_2", 0]]},
        {"id": "MUL_1", "op": "FPMUL", "deps": [["ADD_1", 0]]},
        {"id": "ADD_0", "op": "FPADD", "read_bank": 0, "write_bank": 7, "deps": [["MUL_1", 0]]}
    ]
    
    print(f"[RUN] SMT Performance Audit for Bank-0 Pinning...")
    result = compiler.compile(dsl)
    
    if result["status"] == "SAT":
        print(f"--- PERFORMANCE ACHIEVED ---")
        print(f"   Final II = {result['ii']} (Strictly Limited by Bank 0 Ports)")
    else:
        print(f"❌ ERROR: Physical Conflict Detected. Status: {result.get('status')}")

if __name__ == "__main__":
    run_bank0_anchor_test()
