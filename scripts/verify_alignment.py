import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def run_alignment():
    manifest = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/02_Specs/Hardware_Manifest.json'))
    chain_dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/tests/ground_truth_chain.json'))
    
    parser = SMTDSLParser(manifest)
    parser.load_instructions(chain_dsl)
    
    # Attempt to solve for II=1 (The Limit)
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print("[SUCCESS] Solver SUCCEEDED for II=1")
        viz = SMTVisualizer(result)
        print(viz.render_gantt())
    else:
        print("[FAILED] Solver FAILED for II=1. Calculating minimal II...")
        result_min = parser.solve_modulo(initial_ii=1)
        if result_min:
            print(f"Minimal possible II found: {result_min['ii']}")
            viz = SMTVisualizer(result_min)
            print(viz.render_gantt())

if __name__ == "__main__":
    run_alignment()
