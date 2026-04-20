import os
import sys
import subprocess
import re
import time

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
    print("\n--- Running Semantic Causality Audit ---")
    sprint_path = 'flow/03_Active_Sprints/'
    spec_path = 'flow/02_Specs/'
    app_path = 'app/'
    
    # 1. 识别所有活跃任务
    active_tasks = set()
    if os.path.exists(sprint_path):
        for f in os.listdir(sprint_path):
            m = re.search(r'Task-\d+', f)
            if m: active_tasks.add(m.group(0))
    
    if not active_tasks:
        print_result("Active Tasks Scanned", True, "No active tasks found in flow/03")
        return True

    all_consistent = True
    for tid in active_tasks:
        print(f"\n[Audit] {tid}:")
        
        # 寻找对应的规格书
        specs = [f for f in os.listdir(spec_path) if tid in f] if os.path.exists(spec_path) else []
        spec_ok = len(specs) > 0
        spec_mtime = 0
        if spec_ok:
            spec_file = os.path.join(spec_path, specs[0])
            spec_mtime = os.path.getmtime(spec_file)
            print_result(f"  Spec Alignment", True, f"Linked to {specs[0]}")
        else:
            print_result(f"  Spec Alignment", False, "Missing related Spec in flow/02")
            all_consistent = False

        # 寻找对应的代码实现
        code_files = []
        for root, _, files in os.walk(app_path):
            for f in files:
                full_p = os.path.join(root, f)
                with open(full_p, 'r', encoding='iso-8859-1') as cf:
                    if tid in cf.read():
                        code_files.append((f, os.path.getmtime(full_p)))
        
        if code_files:
            for cf_name, cf_mtime in code_files:
                # 关键：时间戳漂移检测 (Causality Drift)
                if spec_ok and cf_mtime > spec_mtime + 60: # 1分钟宽限期
                    print_result(f"  Code Sync ({cf_name})", False, "WARNING: Code is newer than Spec! Potential logic slip.")
                    all_consistent = False
                else:
                    print_result(f"  Code Sync ({cf_name})", True, "Aligned with Spec timestamp")
        else:
            print_result(f"  Implementation", True, "Task-only (No code signatures yet)")

    return all_consistent

def run_physical_audit():
    print("\n--- Running Physical Truth Audit ---")
    try:
        result = subprocess.run(['python3', 'scripts/final_render.py'], capture_output=True, text=True)
        if "[PASS]" in result.stdout:
            print_result("Physical Compliance", True, "Schedule verified at II=3")
            return True
        else:
            print_result("Physical Compliance", False, "Audit script failed or logic drift detected")
            return False
    except Exception as e:
        print_result("Physical Compliance", False, f"Audit script error: {str(e)}")
        return False

def main():
    print("💠 AOS 2.3 [Industrial Baseline] Semantic Diagnostic\n")
    checks = [
        check_environment(),
        check_repo_structure(),
        check_mission_dna(),
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
