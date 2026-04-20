import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from smt_dsl_parser import SMTDSLParser
from pseudo_gen import generate_reports

def main():
    print("🚀 AOS 3.5 [II=1] Macro-Vector FMA Challenge")
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    dsl_path = "flow/01_Ideation_Threads/TSK-010_DSL.json"
    
    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl_path)
    
    # 强制搜索 II=1 (Single Instruction Bundle)
    # 我们知道 DLY 已经对齐了，所以 II=1 应该是可行的。
    result = parser.solve_modulo(initial_ii=1, max_ii=1)
    
    if result:
        print(f"✅ SUCCESS! Single-Instruction Macro-Compression Certified (II=1).")
        result["metadata"]["spec_dna"] = "TSK-010"
        
        output_path = "flow/03_Output/TSK-010_Result.json"
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        # Call Reports Generator
        report = generate_reports(output_path, manifest_path)
        with open("flow/03_Output/Add10_PseudoCode.txt", "w") as f:
            f.write(report)
        print(f"💾 PseudoCode report updated with II=1 Macro-instructions.")
    else:
        print("❌ FAILED: II=1 is not feasible with current constraints or DLY alignment.")

if __name__ == "__main__":
    main()
