
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def run_madd_professional():
    manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/02_Specs/Hardware_Manifest.json'))
    dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), '../flow/01_Ideation_Threads/MADD_Arr10_DSL.json'))
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl)
    
    print("🚀 [AOS 2.6] Solving MADD (torch.add) with Full Bank Constraints...")
    # 从 II=1 开始寻找物理最优解
    result = parser.solve_modulo(initial_ii=1)
    
    if result:
        print(f"✅ [SUCCESS] Optimal II Found: {result['ii']}")
        viz = SMTVisualizer(result, manifest)
        
        # 使用项目原生的横向可视化 (展示 10 次迭代)
        print("\n=== SMT Unit-Timeline (Multi-Iter Horizontal View) ===")
        print(viz.render_multi_iter_timeline(num_iters=10))
    else:
        print("❌ [FAILED] No valid schedule found for MADD.")

if __name__ == "__main__":
    run_madd_professional()
