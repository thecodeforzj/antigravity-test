import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def run_benchmark():
    manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/02_Specs/Hardware_Manifest.json'))
    dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/01_Ideation_Threads/Taylor3_Arr10_DSL.json'))
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl)
    
    print("[INIT] Searching for optimal Initiation Interval...")
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print(f"[SUCCESS] Optimal II Found: {result['ii']}")
        viz = SMTVisualizer(result, manifest)
        print("\n=== SMT Unit-Timeline (Horizontal View) ===")
        print(viz.render_detailed_timeline(max_cycle=18))
        
        print("\n" + viz.render_gantt())
    else:
        print("[FAILED] No valid schedule found.")

if __name__ == "__main__":
    run_benchmark()
