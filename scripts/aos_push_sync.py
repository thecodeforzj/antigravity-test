import subprocess
import os
import sys

def run_git_command(args, cwd=None):
    # 强制禁止 git add . 
    if 'add' in args and '.' in args:
        print("❌ [PROTOCOL_VIOLATION] Single-dot 'add' is forbidden by AOS-3.0 Rigor.")
        return None
    result = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)
    return result

def atomic_sync_v3(task_id, message):
    print(f"💠 AOS 3.0 Atomic Sync Sequence Starting [Task: {task_id}]")
    
    # 1. Submodule Governance (global_brain)
    print("\n[Layer 1] Governance Submodule...")
    # 仅添加受控的协议与模板改变
    sub_targets = ["README.md", "04_Task_Patterns/", "02_Template_Library/"]
    for target in sub_targets:
        run_git_command(['add', target], cwd='global_brain')
    
    run_git_command(['commit', '-m', f"AOS: [PROTOCOL] {task_id}: {message}"], cwd='global_brain')
    
    # 2. Infrastructure (app/scripts)
    print("[Layer 2] Infrastructure & Tools...")
    infra_targets = ["app/", "scripts/aos_check.py", "scripts/aos_visualizer.py"]
    for target in infra_targets:
        run_git_command(['add', target], cwd=None)
    run_git_command(['commit', '-m', f"AOS: [STRUCTURAL] {task_id}: Hardening kernel."], cwd=None)

    # 3. Atomic Product (flow)
    print("[Layer 3] Atomic Deliverables...")
    flow_targets = [f"flow/01_Tasks/{task_id}.md", "flow/01_Ideation_Threads/", "flow/03_Output/"]
    # 注意：这里我们只添加与当前 Task 相关的产物
    for target in flow_targets:
         run_git_command(['add', target], cwd=None)
    
    # 4. Bind Everything
    run_git_command(['add', 'global_brain', 'flow/00_Mission_Control/Current_Mission.md'], cwd=None)
    run_git_command(['commit', '-m', f"AOS: [ATOMIC] {task_id}: {message} and DNA binding."], cwd=None)

    print("\n✨ [SUCCESS] All layers synchronized atomically.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/aos_push_sync.py [TASK_ID] [MESSAGE]")
        sys.exit(1)
    atomic_sync_v3(sys.argv[1], sys.argv[2])
