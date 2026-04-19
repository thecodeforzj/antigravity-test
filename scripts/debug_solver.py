import sys
import os
import json
from z3 import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_modulo_core import SMTModuloScheduler

def debug():
    m_path = 'flow/02_Specs/Hardware_Manifest.json'
    d_path = 'flow/01_Ideation_Threads/Taylor2_DSL.json'
    
    scheduler = SMTModuloScheduler(m_path)
    with open(d_path, 'r') as f:
        dsl = json.load(f)
    
    raw_deps = []
    for inst in dsl:
        scheduler.add_instruction(inst["id"], inst["op"], inst.get("bank"))
        for d_id, dly in inst.get("deps", []):
            raw_deps.append((inst["id"], d_id, dly))
            
    print(f"--- Debugging II=3 ---")
    ii = 3
    res = scheduler.solve_optimized(ii, raw_deps)
    if res:
        print("SUCCESS")
    else:
        print("FAILED. Checking for logic errors...")
        # Add simpler version to see where it breaks
        s = Solver()
        # Copy-paste logic here for isolation
        # ... (skipping full copy for brevity, will run and check error)

if __name__ == "__main__":
    debug()
