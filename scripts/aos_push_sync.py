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

    # 1.5 强制流水线硬切断 (AOS 3.5 Hard-Gating)
    print(f"\n[Layer 0] Governance Gatekeeper: Formal Audit...")
    audit_cmd = [sys.executable, "scripts/aos_check.py", "--task", task_id]
    audit_res = subprocess.run(audit_cmd, capture_output=True, text=True)
    
    if audit_res.returncode != 0:
        print(f"❌ [BLOCK] Governance Audit Failed for {task_id}.")
        print(audit_res.stdout)
        sys.exit(1)
    
    cert_path = f"flow/03_Output/{task_id}_Audit_Certificate.json"
    if not os.path.exists(cert_path):
        print(f"❌ [BLOCK] Audit Certificate missing! Sync aborted.")
        sys.exit(1)
    print(f"✅ Audit Certificate Verified: {cert_path}")

    # 2. Submodule (global_brain)
    # ... rest of the code ...
    print("\n[Layer 1] Governance Submodule (global_brain)...")
    run_git_command(['add', '.'], cwd='global_brain') 
    run_git_command(['commit', '-m', f"[PROTOCOL] {task_id}: SOP Sealing."], cwd='global_brain')
    
    # 3. Main Repo (Atomic List Only)
    print("\n[Layer 2] Executing Precise Main-Repo Sync...")
    for art in artifacts:
        # 即使文件在本地被删除，也要尝试阶段性提交其删除状态 (git add 会自动处理已跟踪文件的删除)
        run_git_command(['add', art])
        if os.path.exists(art):
            print(f"   Staged: {art}")
        else:
            print(f"   Staged (Deletion): {art}")

    # 4. Mandatory Constitutional Files
    run_git_command(['add', 'global_brain', 'flow/00_Mission_Control/Current_Mission.md', task_card, cert_path])
    
    # 5. Commit
    run_git_command(['commit', '-m', f"AOS: [{task_id}] {message}"])
    print(f"\n✨ [SUCCESS] Task sealed with Audit Certificate: {cert_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/aos_push_sync.py [TASK_ID] [MESSAGE]")
        sys.exit(1)
    atomic_sync_v4(sys.argv[1], sys.argv[2])
