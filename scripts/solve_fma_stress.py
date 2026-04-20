import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from smt_dsl_parser import SMTDSLParser
from pseudo_gen import generate_pseudo_code

def main():
    print("🚀 AOS 3.5 Vector-FMA (10-input) High-Pressure Solver")
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    dsl_path = "flow/01_Ideation_Threads/TSK-009_DSL.json"
    
    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl_path)
    
    # 启用解算
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print(f"✅ SAT! Optimal II={result['ii']}")
        # Inject task_id for pseudo_gen
        result["metadata"]["spec_dna"] = "TSK-009"
        
        output_path = "flow/03_Output/TSK-009_Result.json"
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        # Call Pseudo Generator
        report = generate_pseudo_code(output_path, manifest_path)
        with open("flow/03_Output/Add10_PseudoCode.txt", "w") as f:
            f.write(report)
        print(f"💾 Regression Results & PseudoCode are ready.")
    else:
        print("❌ UNSAT")

if __name__ == "__main__":
    main()
