import subprocess
import os
import time

def run_test(test_file):
    print(f"   Running {test_file}...")
    res = subprocess.run(['python3', test_file], capture_output=True, text=True)
    return res.returncode == 0, res.stdout

def full_audit():
    print("💠 AOS FULL INTEGRATION AUDIT (MBSE Stable Mode)")
    print("="*50)
    
    # 1. Basic Compliance
    print("📍 [STAGE 1] Basic System Compliance")
    res = subprocess.run(['python3', 'scripts/aos_check.py'], capture_output=True, text=True)
    if "[HEALTHY]" not in res.stdout:
        print("❌ FAILED: Basic system check failed.")
        return False
    print("✅ Passed.")

    # 2. Regression Tests
    print("\n📍 [STAGE 2] Full Regression Testing")
    test_dir = 'app/tests/'
    all_tests = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith('.py')]
    
    success_count = 0
    for t in all_tests:
        ok, log = run_test(t)
        if ok:
            print(f"      \033[92m[PASS]\033[0m {os.path.basename(t)}")
            success_count += 1
        else:
            print(f"      \033[91m[FAIL]\033[0m {os.path.basename(t)}")
            print(log)

    # 3. Final Summary
    print("\n" + "="*50)
    print(f"TOTAL TESTS: {len(all_tests)}")
    print(f"PASSED: {success_count}")
    
    if success_count == len(all_tests):
        print("\n\033[92m👑 [AUDIT PASS] System is bit-exact and stable. Authorized for [MERGE].\033[0m")
        return True
    else:
        print("\n\033[91m⛔ [AUDIT FAIL] Regressions detected. Merge BLOCKED.\033[0m")
        return False

if __name__ == "__main__":
    full_audit()
