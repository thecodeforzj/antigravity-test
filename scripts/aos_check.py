import os
import sys
import subprocess
import re
import time
import hashlib

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

def check_repo_structure():
    required_dirs = ['app', 'flow', 'global_brain', 'scripts']
    all_pass = True
    for d in required_dirs:
        status = os.path.isdir(d)
        print_result(f"Directory: {d}/", status)
        if not status: all_pass = False
    
    sub_git = os.path.exists('global_brain/.git')
    print_result("Submodule: global_brain", sub_git, "Incomplete clone?" if not sub_git else "")
    return all_pass and sub_git

def check_mission_dna():
    mission_path = 'flow/00_Mission_Control/Current_Mission.md'
    if not os.path.exists(mission_path):
        print_result("Mission DNA", False, "Current_Mission.md not found")
        return False
    
    with open(mission_path, 'r', encoding='utf-8') as f:
        content = f.read()
        rigor = re.search(r'rigor_level:\s*"(.*?)"', content)
        verification = re.search(r'verification:\s*"(.*?)"', content)
        
        status = rigor and rigor.group(1) == "CRITICAL"
        print_result("DNA: Rigor Level", status, f"Found: {rigor.group(1) if rigor else 'None'}")
        
        v_status = verification and verification.group(1) == "FORMAL"
        print_result("DNA: Verification Mode", v_status, f"Found: {verification.group(1) if verification else 'None'}")
        
    return status and v_status

def find_task_ids_in_dir(path):
    task_ids = set()
    if not os.path.exists(path): return task_ids
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.md', '.py', '.json')):
                with open(os.path.join(root, file), 'r', encoding='iso-8859-1') as f:
                    content = f.read()
                    matches = re.findall(r'Task-\d+', content)
                    for m in matches: task_ids.add(m)
    return task_ids

def check_task_causality():
    print("\n--- Running Semantic Causality Audit (V2.6) ---")
    task_path = 'flow/01_Tasks/'
    spec_path = 'flow/02_Specs/'
    
    active_tasks = []
    if os.path.exists(task_path):
        active_tasks = [f.split('.')[0] for f in os.listdir(task_path) if f.endswith('.md')]
    
    if not active_tasks:
        print_result("Active Tasks Scanned", True, "No task cards found in flow/01")
        return True

    all_consistent = True
    for tid in active_tasks:
        print(f"\n[Audit] {tid}:")
        # 寻找规格书 (兼容 TSK 和 Task 前缀)
        normalized_tid = tid.replace('TSK', 'Task')
        specs = [f for f in os.listdir(spec_path) if tid in f or normalized_tid in f] if os.path.exists(spec_path) else []
        
        if specs:
            print_result(f"  Spec Alignment", True, f"Linked to {specs[0]}")
        else:
            print_result(f"  Spec Alignment", False, "Missing related Spec in flow/02")
            all_consistent = False
    return all_consistent

def run_physical_audit():
    print("\n--- Running Universal Physical Truth Audit (V2.6) ---")
    output_dir = 'flow/03_Output/'
    if not os.path.exists(output_dir): return True
    
    all_pass = True
    results = [f for f in os.listdir(output_dir) if f.endswith('_Result.json')]
    for r in results:
        base_name = r.replace('_Result.json', '')
        # 匹配其 DSL 文件
        dsl_file = f"flow/01_Ideation_Threads/{base_name}_DSL.json"
        if not os.path.exists(dsl_file): continue
        
        cmd = ['python3', 'scripts/final_truth_scanner.py', os.path.join(output_dir, r), 'flow/02_Specs/Hardware_Manifest.json', dsl_file]
        run = subprocess.run(cmd, capture_output=True, text=True)
        if "[PASS]" in run.stdout:
            print_result(f"Truth Compliance: {base_name}", True)
        else:
            print_result(f"Truth Compliance: {base_name}", False, "Logic Drift or Sync Error")
            all_pass = False
    return all_pass

def get_file_hash(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_truth_fingerprints():
    print("\n--- Running Truth Fingerprint Audit (V2.6) ---")
    mission_path = 'flow/00_Mission_Control/Current_Mission.md'
    with open(mission_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 动态解析 DNA-Fingerprint
    fingerprints = re.findall(r'DNA-Fingerprint:\s*([^|]+)\|([a-f0-9]+)', content)
    
    all_matched = True
    for name, recorded_hash in fingerprints:
        # 推断物理路径
        path = None
        if name == "Hardware_Manifest": path = "flow/02_Specs/Hardware_Manifest.json"
        elif name == "AOS_Rules": path = ".antigravity_rules"
        elif name == "SMT_Scheduler_Detailed_Specs": path = "flow/02_Specs/SMT_Scheduler_Detailed_Specs.md"
        elif "Spec" in name: 
            # 兼容其他带有 Spec 字样的文件
            s_name = name.replace('_Spec', '').replace('MADD', 'Task-002_MADD')
            path = f"flow/02_Specs/{s_name}_Spec.md"
        
        if path and os.path.exists(path):
            current = get_file_hash(path)
            if current == recorded_hash:
                print_result(f"DNA Verified: {name}", True)
            else:
                print_result(f"DNA Drift: {name}", False, "TAMPERED!")
                all_matched = False
        else:
            print_result(f"DNA Missing: {name}", False, f"Path unknown or missing: {path}")
            all_matched = False
    return all_matched

def main():
    print("💠 AOS 2.5 [Truth Guardian] Advanced Diagnostic\n")
    checks = [
        check_environment(),
        check_repo_structure(),
        check_mission_dna(),
        check_truth_fingerprints(), # 新增指纹校验
        check_task_causality(),
        run_physical_audit()
    ]
    
    print("\n" + "="*50)
    if all(checks):
        print("\033[92m[HEALTHY] 系统状态：优。因果对齐，无语义断层。\033[0m")
    else:
        print("\033[91m[UNHEALTHY] 系统状态：存在偏差。存在任务遗漏或同步断层！\033[0m")
    print("="*50)

if __name__ == "__main__":
    main()
