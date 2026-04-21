import json
import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_modulo_core import SMTModuloScheduler

def debug_ii5():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    scheduler = SMTModuloScheduler(manifest_path)
    
    # Horner-3 Vector Core
    dsl_insts = [
        {"id": "MUL_3", "unit": "FPMUL", "read_bank": 0, "latency": 4},
        {"id": "ADD_2", "unit": "FPADD", "read_bank": 0, "latency": 4},
        {"id": "MUL_2", "unit": "FPMUL", "latency": 4},
        {"id": "ADD_1", "unit": "FPADD", "read_bank": 0, "latency": 4},
        {"id": "MUL_1", "unit": "FPMUL", "latency": 4},
        {"id": "ADD_0", "unit": "FPADD", "read_bank": 0, "write_bank": 7, "latency": 4}
    ]
    deps = [
        ("ADD_2", "MUL_3", 0),
        ("MUL_2", "ADD_2", 0),
        ("ADD_1", "MUL_2", 0),
        ("MUL_1", "ADD_1", 0),
        ("ADD_0", "MUL_1", 0)
    ]
    
    scheduler.instructions = dsl_insts
    # Re-bind Z3 variables
    from z3 import Int
    for i in scheduler.instructions:
        i["t_var"] = Int(f"t_{i['id']}")
        i["u_idx"] = Int(f"u_idx_{i['id']}")

    print(">>> AOS PERFORMANCE PROBE: Investigating II=5 Unsat Reasons")
    res = scheduler.solve_modulo(5, deps)
    
    if res["status"] == "SAT":
        print("✅ Corrected! II=5 IS reachable.")
    else:
        print(f"❌ II=5 Still UNSAT.")
        # Attempt to display simplified unsat core if possible
        pass

if __name__ == "__main__":
    debug_ii5()
