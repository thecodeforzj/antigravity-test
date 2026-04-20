import subprocess
import os
import sys

def run_git_command(args, cwd=None):
    result = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)
    return result

def check_aos_health():
    print("🔍 [AOS Audit] Running pre-commit health check...")
    res = subprocess.run(['python3', 'scripts/aos_check.py'], capture_output=True, text=True)
    if "[HEALTHY]" not in res.stdout:
        print("❌ [BLOCKED] System is UNHEALTHY. Fix semantic gaps before committing.")
        print(res.stdout)
        return False
    print("✅ [AOS Audit] System is healthy. Proceeding to sync.")
    return True

def atomic_sync(message):
    if not check_aos_health():
        return

    # 1. Check Submodule (global_brain)
    print("\n📦 [Submodule] Checking global_brain...")
    status_sub = run_git_command(['status', '--porcelain'], cwd='global_brain')
    if status_sub.stdout.strip():
        print("   Found changes in global_brain. Committing...")
        run_git_command(['add', '.'], cwd='global_brain')
        run_git_command(['commit', '-m', f"[PROTOCOL] {message}"], cwd='global_brain')
    else:
        print("   No changes in global_brain.")

    # 2. Check Main Repo
    print("\n🚀 [Main Repo] Checking kernel updates...")
    status_main = run_git_command(['status', '--porcelain'])
    if status_main.stdout.strip():
        print("   Found changes in main repo. Committing...")
        run_git_command(['add', '.'], cwd=None)
        run_git_command(['commit', '-m', f"[KERNEL] {message}"], cwd=None)
    else:
        print("   No changes in main repo.")

    print("\n✨ Atomic Sync Complete. Ready to push.")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Standard incremental update"
    atomic_sync(msg)
