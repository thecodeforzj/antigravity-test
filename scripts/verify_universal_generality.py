import json
import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler

def verify_generality():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS V5.8 UNIVERSAL GENERALITY AUDIT\n")
    
    # 场景 A: 复杂菱形算子 (Diamond) + 40 路输入
    diamond_task = {
        "metadata": {"total_inputs": 40, "vector_width": 4},
        "instructions": [
            {"id": "A", "op": "FPMUL", "read_bank": 0},
            {"id": "B", "op": "FPADD", "deps": [["A", 0]]},
            {"id": "C", "op": "FPADD", "deps": [["A", 0]]},
            {"id": "D", "op": "FPMUL", "deps": [["B", 0], ["C", 0]], "write_bank": 7}
        ]
    }
    
    # 场景 B: 极深串行链 (6-Stage Chain) + 100 路输入
    chain_task = {
        "metadata": {"total_inputs": 100, "vector_width": 4},
        "instructions": [
            {"id": "C1", "op": "FPMUL", "read_bank": 0},
            {"id": "C2", "op": "FPADD", "deps": [["C1", 0]]},
            {"id": "C3", "op": "FPMUL", "deps": [["C2", 0]]},
            {"id": "C4", "op": "FPADD", "deps": [["C3", 0]]},
            {"id": "C5", "op": "FPMUL", "deps": [["C4", 0]]},
            {"id": "C6", "op": "FPADD", "deps": [["C5", 0]], "write_bank": 7}
        ]
    }
    
    for name, task in [("DIAMOND-40", diamond_task), ("CHAIN-100", chain_task)]:
        print(f"--- TEST CASE: {name} ---")
        res = compiler.compile(task)
        if res["status"] == "SAT":
            h = res["header"]
            print(f"SUCCESS: II={res['ii']}, LOOP_COUNT={h['LOOPS']}, INC={h['INC']}")
        else:
            print(f"FAILED: {res.get('reason')}")
        print()

if __name__ == "__main__":
    verify_generality()
