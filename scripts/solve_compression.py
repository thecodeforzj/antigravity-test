import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from smt_dsl_parser import SMTDSLParser

def main():
    print("💠 AOS 3.5 Instruction Compression Solver Test")
    manifest = "global_brain/04_Task_Patterns/Pattern_Modulo_Kernel.md" # We use a standard manifest or mock one
    # Note: We need a valid hardware manifest. Let's use the default one if it exists or define a mock.
    # Actually, the user project seems to use specific manifests.
    
    # Check if we have a hardware manifest
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    if not os.path.exists(manifest_path):
        print(f"❌ Missing hardware manifest at {manifest_path}")
        return

    parser = SMTDSLParser(manifest_path)
    dsl_path = "flow/01_Ideation_Threads/Compression_Test_DSL.json"
    parser.load_instructions(dsl_path)
    
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print(f"✅ SAT! II={result['ii']}")
        print(json.dumps(result["schedule"], indent=2))
        with open("flow/03_Output/Compression_Test_Result.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 Result saved to flow/03_Output/Compression_Test_Result.json")
    else:
        print("❌ UNSAT")

if __name__ == "__main__":
    main()
