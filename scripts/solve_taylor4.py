
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def run_taylor4_professional():
    manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/02_Specs/Hardware_Manifest.json'))
    dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/01_Ideation_Threads/Taylor4_MADD_Style_DSL.json'))
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl)
    
    print("🚀 [AOS 3.0] Solving Taylor 4th Order with MADD Process (Native Rigor)...")
    # 模拟 10 个批次的展开，寻找全流水最优解
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print(f"✅ [SUCCESS] Optimal II Found: {result['ii']}")
        
        # 🟢 AOS 3.0: 持久化受控产物
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/03_Output/Taylor4_MADD_Style_Result.json'))
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Result saved to {os.path.basename(output_path)}")

        viz = SMTVisualizer(result, manifest)
        print("\n=== SMT Unit-Timeline (Taylor4 10-Element Full-Pipe View) ===")
        print(viz.render_multi_iter_timeline(num_iters=10))
    else:
        print("❌ [FAILED] No valid schedule found for Taylor4.")

if __name__ == "__main__":
    run_taylor4_professional()
