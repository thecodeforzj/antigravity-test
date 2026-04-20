import os
import sys
import subprocess
import re
import time
import hashlib
import json

def print_result(check_name, status, message=""):
    color = "\033[92m[PASS]\033[0m" if status else "\033[91m[FAIL]\033[0m"
    if not status and "WARNING" in message:
        color = "\033[93m[WARN]\033[0m"
    print(f"{color} {check_name:30} {message}")

def check_environment():
    try:
        import z3
        print_result("Z3 Solver Core", True, f"Version: {z3.get_version_string()}")
    except ImportError:
        print_result("Z3 Solver Core", False, "Missing z3-solver. Run 'pip install z3-solver'")
        return False
    return True

def get_file_hash(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_physic_causal_chains():
    print("\n--- Running V3.0 Physical Causal-Chain Audit ---")
    all_pass = True
    output_dir = 'flow/03_Output/'
    if not os.path.exists(output_dir): return True
    
    results = [f for f in os.listdir(output_dir) if f.endswith('_Result.json')]
    for r in results:
        task_name = r.replace('_Result.json', '')
        # 智能匹配可能的 DSL 文件名
        potential_dsls = [
            f"flow/01_Ideation_Threads/{task_name}.json",
            f"flow/01_Ideation_Threads/{task_name}_DSL.json",
            f"flow/01_Ideation_Threads/{task_name}_Arr10_DSL.json",
            f"flow/01_Ideation_Threads/{task_name.replace('_DSL', '')}_DSL.json"
        ]
        dsl_file = next((d for d in potential_dsls if os.path.exists(d)), None)
        
        if dsl_file:
            with open(os.path.join(output_dir, r), 'r') as f:
                res_meta = json.load(f).get("metadata", {})
                stored_hash = res_meta.get("dsl_hash")
            
            current_hash = get_file_hash(dsl_file)
            if current_hash != stored_hash:
                print_result(f"Causal Link: {task_name}", False, "CRITICAL: DSL modified after solving!")
                all_pass = False
            else:
                print_result(f"Causal Link: {task_name}", True, f"DNA Matched (via {os.path.basename(dsl_file)})")
        else:
            print_result(f"Causal Link: {task_name}", False, "ORPHAN: No DSL source found")
            all_pass = False
    return all_pass

def check_truth_fingerprints():
    print("\n--- Running V3.0 Truth Fingerprint Audit ---")
    mission_path = 'flow/00_Mission_Control/Current_Mission.md'
    if not os.path.exists(mission_path): return False
    with open(mission_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fingerprints = re.findall(r'DNA-Fingerprint:\s*([^| \n]+)\|([a-f0-9]+)', content)
    all_matched = True
    
    # 物理路径映射库 (真理基准)
    paths = {
        "Hardware_Manifest": "flow/02_Specs/Hardware_Manifest.json",
        "AOS_Rules": ".antigravity_rules",
        "AOS_Manifest": "global_brain/03_AOS_Core/Agent_System_Manifest.md",
        "SMT_Scheduler_Detailed_Specs": "flow/02_Specs/SMT_Scheduler_Detailed_Specs.md",
        "MADD_Spec": "flow/02_Specs/Task-002_MADD_Spec.md",
        "Boundary_Spec": "flow/02_Specs/Task-003_Boundary_Spec.md",
        "Taylor4_Spec": "flow/02_Specs/Task-004_Taylor4_Spec.md"
    }

    for name, recorded_hash in fingerprints:
        path = paths.get(name)
        if path and os.path.exists(path):
            current = get_file_hash(path)
            if current == recorded_hash:
                print_result(f"Lace-up DNA: {name}", True)
            else:
                print_result(f"Lace-up DNA: {name}", False, "CRITICAL: Truth Drift!")
                all_matched = False
        else:
            print_result(f"Lace-up DNA: {name}", False, f"Path unknown/missing: {path}")
            all_matched = False
    return all_matched

def check_hardware_field_coverage(task_id):
    print(f"\n--- Running V3.5 Physical Coverage Audit [Task: {task_id}] ---")
    
    # 1. 定位 Spec 与 DSL (AOS 3.5 泛化逻辑)
    spec_mapping = {
        "TSK-006": "flow/02_Specs/Instruction_Compression_Spec.md",
        "TSK-007": "flow/02_Specs/TSK-007_Spec.md",
        "TSK-008": "flow/02_Specs/TSK-008_Spec.md",
    }
    
    spec_path = spec_mapping.get(task_id) or f"flow/02_Specs/{task_id}_Spec.md"
    dsl_pattern = f"flow/01_Ideation_Threads/{task_id.replace('TSK-0', 'Compression_Test')}_DSL.json" if task_id == "TSK-006" else f"flow/01_Ideation_Threads/{task_id}_DSL.json"

    # 如果是标准的 Compression_Test 命名
    if task_id == "TSK-006":
        dsl_pattern = "flow/01_Ideation_Threads/Compression_Test_DSL.json"

    if not spec_path or not os.path.exists(spec_path):
        print_result("Physical Coverage", False, "Missing Spec for coverage scanning.")
        return False
        
    # 2. 从 Spec 中抓取字段定义 (Markdown Table 解析)
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    # 提取表格中加粗的字段名，例如 | **VLD** |
    required_fields = set(re.findall(r'\|\s*\*\*([A-Z_0-9]+)\*\*\s*\|', spec_content))
    if not required_fields:
        print_result("Physical Coverage", True, "No mandatory bitfields found in Spec.")
        return True

    print(f"🔍 Spec defined {len(required_fields)} mandatory fields: {required_fields}")

    # 3. 检查 DSL 覆盖率
    if not os.path.exists(dsl_pattern):
        print_result("Physical Coverage", False, f"DSL file {dsl_pattern} not found.")
        return False

    with open(dsl_pattern, 'r', encoding='utf-8') as f:
        dsl_data = json.load(f)
    
    covered_fields = set()
    for inst in dsl_data:
        # 🟢 AOS 3.5: Case-insensitive field discovery
        inst_keys = {k.upper() for k in inst.keys()}
        for field in required_fields:
            if field.upper() in inst_keys:
                covered_fields.add(field.upper())

    missing = required_fields - covered_fields
    coverage = len(covered_fields) / len(required_fields) * 100

    if missing:
        print_result("Physical Coverage", False, f"Coverage: {coverage:.1f}%. Missing fields: {missing}")
        return False
    else:
        print_result("Physical Coverage", True, f"100% Coverage Reached.")
        
        # 4. 签发数字证书
        cert = {
            "task_id": task_id,
            "timestamp": time.time(),
            "spec_hash": get_file_hash(spec_path),
            "dsl_hash": get_file_hash(dsl_pattern),
            "coverage": "100%",
            "signer": "AOS_Truth_Guardian_V3.5"
        }
        cert_path = f"flow/03_Output/{task_id}_Audit_Certificate.json"
        with open(cert_path, 'w') as f:
            json.dump(cert, f, indent=2)
        print(f"📜 Certificate signed: {cert_path}")
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Target Task ID for coverage audit")
    args = parser.parse_args()

    print("💠 AOS 3.5 [Truth Guardian] Advanced Verification\n")
    
    checks = [check_environment(), check_truth_fingerprints()]
    
    if args.task:
        checks.append(check_hardware_field_coverage(args.task))
    else:
        checks.append(check_physic_causal_chains())
    
    print("\n" + "="*50)
    if all(checks):
        print("\033[92m[HEALTHY] 系统状态：优。物理因果链与规约覆盖 100% 对齐。\033[0m")
    else:
        sys.exit(1) # 强制熔断中止
    print("="*50)

if __name__ == "__main__":
    main()
