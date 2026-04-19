import sys
import os
import json
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def final_render():
    m_path = 'flow/02_Specs/Hardware_Manifest.json'
    d_path = 'flow/01_Ideation_Threads/Taylor3_Arr10_DSL.json'
    res_path = 'flow/03_Output/Taylor3_Result.json'
    
    with open(m_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    parser = SMTDSLParser(m_path)
    parser.load_instructions(d_path)
    
    print("[INIT] Starting Taylor3 Production Run...", flush=True)
    
    ii = 1
    while ii < 32:
        print(f"[SEARCH] Testing II = {ii}...", end=" ", flush=True)
        # We now go straight to optimized search with strict-compact true 
        # to ensure we follow the constraints added in the core.
        result = parser.solve_modulo(ii)
        
        if result:
            print("SAT!", flush=True)
            # 1. SAVE TO JSON FOR SCANNER
            with open(res_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)
            
            # 2. RUN PHYSICAL TRUTH SCANNER
            print("[AUDIT] Invoking Independent Truth Scanner...", flush=True)
            audit_proc = subprocess.run([sys.executable, 'scripts/final_truth_scanner.py'], capture_output=True, text=True)
            print(audit_proc.stdout)
            
            if "[PASS]" in audit_proc.stdout:
                viz = SMTVisualizer(result, manifest)
                output = viz.render_multi_iter_timeline(num_iters=10)
                print(output)
                return
        else:
            print("UNSAT.", flush=True)
        ii += 1

if __name__ == "__main__":
    final_render()
