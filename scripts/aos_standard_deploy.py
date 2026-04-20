
import sys
import os
import json
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from smt_dsl_parser import SMTDSLParser
from smt_visualizer import SMTVisualizer

def deploy_new_kernel(dsl_name):
    print(f"🚀 [AOS-FACTORY] Deploying New Kernel: {dsl_name}")
    
    # 路径标准化
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    dsl_path = f"flow/01_Ideation_Threads/{dsl_name}.json"
    output_path = f"flow/03_Output/{dsl_name}_Result.json"
    
    if not os.path.exists(dsl_path):
        print(f"❌ [ABORT] DSL file not found: {dsl_path}")
        return

    # 1. 执行物理求解 (Formal Solve)
    print("--- Phase 1: SMT Formal Solving ---")
    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl_path)
    result = parser.solve_modulo(initial_ii=1)
    
    if not result:
        print("❌ [FAIL] No physical solution found.")
        return

    # 2. 写入结果并自动对齐哈希
    with open(dsl_path, 'rb') as f:
        d_hash = hashlib.sha256(f.read()).hexdigest()
    result['metadata']['dsl_hash'] = d_hash
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    # 3. 自动触发真理审计 (Truth Scan)
    print("--- Phase 2: Mandatory Truth Scan ---")
    audit_cmd = f"python3 scripts/final_truth_scanner.py {output_path} {manifest_path} {dsl_path}"
    audit_res = os.system(audit_cmd)
    
    if audit_res == 0:
        print(f"\n✨ [SUCCESS] Kernel {dsl_name} is now CERTIFIED and DEPLOYED.")
    else:
        print(f"\n🛑 [REJECTED] Kernel {dsl_name} failed Physical Audit. Clean up output.")
        if os.path.exists(output_path): os.remove(output_path) # 物理销毁非认证工件
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/aos_standard_deploy.py <DSL_FILENAME_WITHOUT_EXT>")
    else:
        deploy_new_kernel(sys.argv[1])
