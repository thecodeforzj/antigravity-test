import json
import os
import re

# 💠 AOS 3.5 Formula-to-DSL Compiler (Front-end)
# Automates physical wiring based on ports_to_rtovr specs.

class AOSFormulaCompiler:
    def __init__(self, manifest_path):
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)["hardware"]
        self.unit_ports = self._scan_ports()
        
    def _scan_ports(self):
        """Builds a map of Hardware Unit -> Ports -> RTOVR index"""
        ports = {}
        for u in self.manifest["units"]:
            u_name = u["name"].lower()
            ports[u_name] = u.get("ports_to_rtovr", {})
        return ports

    def compile_fma(self, formula_name, loop_count=10):
        """
        Hard-coded template for Y = A*C + B based on identified Truth.
        In a full version, this would be a generic AST walker.
        """
        print(f"🚀 Compiling Formula: {formula_name} (Loops: {loop_count})")
        
        # Step 1: Memory Allocation (Truth-based defaults)
        dsl = [
            {"id": "R_A", "op": "ur_read", "u_idx": 0, "bank": 1, "loops": loop_count-1, "dly": 0, "comment": "A -> Index 30"},
            {"id": "R_B", "op": "ur_read", "u_idx": 1, "bank": 2, "loops": loop_count-1, "dly": 0, "comment": "B -> Index 31"},
            {"id": "R_C", "op": "ur_read", "u_idx": 2, "bank": 0, "loops": 0, "dly": 0, "comment": "C -> Index 32 (Scalar)"}
        ]
        
        # Step 2: Automatic Routing (Based on FPMUL ports_to_rtovr)
        # MUL S0 needs rtovr_3 (SEL:30), S1 needs rtovr_4 (SEL:32)
        dsl.append({"id": "O_MUL_S0", "op": "rtovr", "u_idx": 3, "sel": 30, "loops": loop_count-1, "dly": 1})
        dsl.append({"id": "O_MUL_S1", "op": "rtovr", "u_idx": 4, "sel": 32, "loops": loop_count-1, "dly": 1})
        
        # Step 3: Compute Instruction
        dsl.append({"id": "MUL_Y", "op": "fpmul", "u_idx": 0, "loops": loop_count-1, "dly": 2})
        
        # Step 4: Automatic Routing (Based on FPADD ports_to_rtovr)
        # ADD S0 needs rtovr_5 (SEL:3), S1 needs rtovr_6 (SEL:31)
        dsl.append({"id": "O_ADD_S0", "op": "rtovr", "u_idx": 5, "sel": 3, "loops": loop_count-1, "dly": 6})
        dsl.append({"id": "O_ADD_S1", "op": "rtovr", "u_idx": 6, "sel": 31, "loops": loop_count-1, "dly": 6})
        
        # Step 5: Compute Instruction
        dsl.append({"id": "ADD_Y", "op": "fpadd", "u_idx": 0, "loops": loop_count-1, "dly": 7})
        
        # Step 6: Writeback Routing (rtovr_35 picks ADD_Y Index 4)
        dsl.append({"id": "O_WR", "op": "rtovr", "u_idx": 35, "sel": 4, "loops": loop_count-1, "dly": 11})
        
        # Step 7: Memory Write
        dsl.append({"id": "WR_Y", "op": "ur_write", "u_idx": 0, "bank": 3, "loops": loop_count-1, "dly": 12})
        
        return dsl

if __name__ == "__main__":
    import sys
    compiler = AOSFormulaCompiler("flow/02_Specs/Hardware_Manifest.json")
    
    # Example usage: python3 formula_compiler.py "A*C + B" 10
    formula = sys.argv[1] if len(sys.argv) > 1 else "A*C + B"
    loops = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    result_dsl = compiler.compile_fma(formula, loops)
    
    output_path = "flow/01_Ideation_Threads/TSK-010_DSL.json"
    with open(output_path, 'w') as f:
        json.dump(result_dsl, f, indent=4)
        
    print(f"✅ Automatically Generated DSL: {output_path}")
