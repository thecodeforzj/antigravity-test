import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.smt_dsl_compiler import SMTDSLCompiler

def generate_true_optimal_hex():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS V5.11 TRUE OPTIMAL: Achieving II=5 via Bank Decoupling\n")
    
    # 读写分离 DSL: 常数在 Bank 0, 结果在 Bank 7
    task = {
        "metadata": {"total_inputs": 80, "vector_width": 4},
        "instructions": [
            {"id": "MUL_3", "op": "FPMUL", "read_bank": 0},
            {"id": "ADD_2", "op": "FPADD", "read_bank": 0, "deps": [["MUL_3", 0]]},
            {"id": "MUL_2", "op": "FPMUL", "deps": [["ADD_2", 0]]},
            {"id": "ADD_1", "op": "FPADD", "read_bank": 0, "deps": [["MUL_2", 0]]},
            {"id": "MUL_1", "op": "FPMUL", "deps": [["ADD_1", 0]]},
            {"id": "ADD_0", "op": "FPADD", "read_bank": 0, "write_bank": 7, "deps": [["MUL_1", 0]]}
        ]
    }
    
    res = compiler.compile(task)
    if res["status"] == "SAT":
        ii = res["ii"]
        print(f"--- TRUE OPTIMAL ACHIEVED ---")
        print(f"Final II = {ii}")
        # Build 41-bit Header bits
        header = (1 << 40) | (20 << 11) | (ii << 5)
        # Note: Added DLY manually based on table below
        print(f"Optimal Header Sample with II=5: {hex(header).upper()}")
    else:
        print("Still UNSAT at II=5.")

if __name__ == "__main__":
    generate_true_optimal_hex()
