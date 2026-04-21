import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.smt_dsl_compiler import SMTDSLCompiler

def generate_ii4_resonance_solution():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS V4.0 STABLE: Achieving II=4 via Resonance Decoupling (Bank 0/7 Separated)\n")
    
    # 3rd Order Horner (80 Inputs, 20 Loops)
    # AX_06 Solution: Constant a3, a2, a1 in Bank 0, Store sum in Bank 7
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
    
    # We force the search to start from II=4
    # The compiler.compile calls scheduler.solve_optimal_ii which does binary search starting from MII
    res = compiler.compile(task)
    
    # --- 📊 GENERATE PIPELINED TRACE (Horner-3 Industrial Style) ---
    num_iters = 10
    total_T = 64
    ii = res["ii"]
    pipelined_viz = compiler.visualizer.generate_pipelined_trace(
        res["schedule"], res["instructions"], ii, num_iters=num_iters, max_cycles=total_T
    )

    output_path = "flow/03_Output/AOS_V4.0_Horner3_Trace.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== AOS V4.0: 3rd Order Horner Expansion Trace ===\n")
        f.write("Algorithm: P(x) = (((a3*x + a2)*x + a1)*x + a0)\n")
        f.write(f"Configuration: 80 Inputs, Vector Width 4 (20 Iterations total), II={ii}\n")
        
        if res["status"] == "SAT":
            f.write(f"\nHORIZONTAL PIPELINE TRACE (Overlap II={ii}):\n")
            f.write("Labels: Iteration.Op (e.g. 0.M3 = Iteration 0, MUL_3)\n\n")
            f.write(pipelined_viz)
            
            f.write("\n\nSCHEDULE MAPPING (Single Iteration Body):\n")
            for rid, t_start in sorted(res["schedule"].items(), key=lambda x: x[1]):
                 f.write(f"  {rid}: Start Cycle = {t_start}\n")
                 
            print(f">>> Horner-3 Trace saved to: {output_path}")
        else:
            f.write(f"FAILURE: {res.get('status')}\n")
            print(f">>> Failure! Detailed log saved to: {output_path}")

if __name__ == "__main__":
    generate_ii4_resonance_solution()
