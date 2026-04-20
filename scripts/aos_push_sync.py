import subprocess
import os
import sys
import re

def run_git_command(args, cwd=None):
    result = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)
    return result

def atomic_sync_v4(task_id, message):
    print(f"💠 AOS 3.5 High-Resolution Atomic Sync [Task: {task_id}]")
    
    # 1. 解析任务卡片中的 [ARTIFACT_INDEX]
    task_card = f"flow/01_Tasks/{task_id}.md"
    if not os.path.exists(task_card):
        print(f"❌ [ABORT] Task card {task_card} not found.")
        return

    with open(task_card, 'r') as f:
        content = f.read()
    
    # 提取所有反引号路径
    artifacts = re.findall(r'`([^`]+)`', content)
    print(f"📦 Identified {len(artifacts)} target artifacts from task card.")

    # 2. Submodule (global_brain)
    # 我们知道 global_brain 的变更是跨任务的，需要独立处理
    print("\n[Layer 1] Governance Submodule (global_brain)...")
    run_git_command(['add', '.'], cwd='global_brain') # 子模块内部依然受控
    run_git_command(['commit', '-m', f"[PROTOCOL] {task_id}: SOP Sealing."], cwd='global_brain')
    
    # 3. Main Repo (Atomic List Only)
    print("\n[Layer 2] Executing Precise Main-Repo Sync...")
    for art in artifacts:
        if os.path.exists(art):
            run_git_command(['add', art])
            print(f"   Staged: {art}")
        else:
            print(f"   ⚠️ Skipping missing artifact: {art}")

    # 4. Mandatory Constitutional Files
    run_git_command(['add', 'global_brain', 'flow/00_Mission_Control/Current_Mission.md', task_card])
    
    # 5. Commit
    run_git_command(['commit', '-m', f"AOS: [{task_id}] {message}"])
    print("\n✨ [SUCCESS] Task atomic state captured and sealed.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/aos_push_sync.py [TASK_ID] [MESSAGE]")
        sys.exit(1)
    atomic_sync_v4(sys.argv[1], sys.argv[2])
