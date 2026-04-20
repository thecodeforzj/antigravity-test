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

def main():
    print("💠 AOS 3.0 [Truth Guardian] Reverse Verification\n")
    # 为了简化，我们只保留核心的物理核验
    checks = [
        check_environment(),
        check_truth_fingerprints(),
        check_physic_causal_chains()
    ]
    
    print("\n" + "="*50)
    if all(checks):
        print("\033[92m[HEALTHY] 系统状态：优。物理因果链 100% 对齐。\033[0m")
    else:
        print("\033[91m[UNHEALTHY] 系统状态：存在偏差。存在非受控的物理漂移！\033[0m")
    print("="*50)

if __name__ == "__main__":
    main()
