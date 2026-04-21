import sys
import os
import json

# Ensure app directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_modulo_core import SMTModuloScheduler

def test_p3_alignment():
    # Force UTF-8 for Windows
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">>> AOS P3 Verification Trace: SMT_Solver_SDD Implementation\n")
    
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    scheduler = SMTModuloScheduler(manifest_path)
    
    # 模拟一个简单的依赖链：A -> B -> C -> D
    # 全都使用 FPMUL (Latency 4)
    # II = 1 时，FPMUL (Count=1) 是饱和的
    scheduler.add_instruction("A", "FPMUL")
    scheduler.add_instruction("B", "FPMUL")
    
    deps = [("B", "A", 0)]
    
    print("[TEST 1] Testing Optimal II Search...")
    # 2个 FPMUL 指令，FPMUL Count=1，II 理论最小值为 2
    result = scheduler.solve_optimal_ii(deps)
    
    if result["status"] == "SAT":
        print(f"✅ Success: Found Optimal II = {result['ii']}")
        print(f"   Schedule: {result['schedule']}")
    else:
        print(f"❌ Fail: Expected Optimal II but got {result}")

    print("\n[TEST 2] Testing Unsat Core (Conflict Traceback)...")
    # 强制 II = 1，此时 2个 FPMUL 必定冲突
    conflict_res = scheduler.solve_modulo(1, deps)
    
    if conflict_res["status"] == "UNSAT" and "unsat_core" in conflict_res:
        print("✅ Success: Correctly identified Unsat Core:")
        for core in conflict_res["unsat_core"]:
            print(f"   - {core}")
    else:
        print(f"❌ Fail: Expected Unsat Core but got {conflict_res}")

if __name__ == "__main__":
    test_p3_alignment()
