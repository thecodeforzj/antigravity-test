import os
import sys
import json
import subprocess
import time

# 💠 AOS 3.11 Full-Coverage Regression Engine
# Function: Multi-Operator Compilation & Scheduling Stress Test

TEST_CASES = [
    {
        "id": "FMA_BASIC",
        "formula": "A*X + B",
        "ii_min": 1,
        "grid": (9, [])
    },
    {
        "id": "ADD10_CHAIN",
        "formula": "A+B+C+D+E+F+G+H+I+J",
        "ii_min": 9,
        "grid": (9, [])
    },
    {
        "id": "HORNER_3RD",
        "formula": "((A3*X + A2)*X + A1)*X + A0",
        "ii_min": 3,
        "grid": (9, [])
    },
    {
        "id": "HORNER_6TH",
        "formula": "((((((A6*X + A5)*X + A4)*X + A3)*X + A2)*X + A1)*X + A0)",
        "ii_min": 6,
        "grid": (9, [(1, 9)])
    }
]

def run_step(cmd, desc):
    print(f"  [RUN] {desc}...", end="", flush=True)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print("\033[92m PASS\033[0m")
        return True, res.stdout
    else:
        print("\033[91m FAIL\033[0m")
        print(res.stderr)
        return False, res.stderr

def main():
    print("🚀 AOS 3.11 Production Regression Suite: SELECTIVE EXECUTION\n" + "="*50)
    
    # 🟢 AOS 3.11.5: Selective Execution CLI
    target_id = sys.argv[1].upper() if len(sys.argv) > 1 else None
    
    active_cases = TEST_CASES
    if target_id:
        active_cases = [c for c in TEST_CASES if c["id"] == target_id]
        if not active_cases:
            print(f"❌ [ABORT] Test Case '{target_id}' not found.")
            print(f"Available cases: {[c['id'] for c in TEST_CASES]}")
            sys.exit(1)
        print(f"🎯 Target Acquired: {target_id}")

    passed = 0
    total = len(active_cases)
    
    for case in active_cases:
        cid = case["id"]
        print(f"\n▶️ CASE: {cid} | Target $II={case['ii_min']}")
        
        # 1. Update formula_compiler bootstrap (Injection)
        # We modify formula_compiler.py's main block temporarily
        # Actually, it's better to just invoke the class if we could, 
        # but for AOS rigor, we use the standard scripts.
        
        # Generator script
        with open("scripts/regression_trigger.py", "w") as f:
            f.write(f"""
import json
from formula_compiler import AOSASTCompiler
compiler = AOSASTCompiler("flow/02_Specs/Hardware_Manifest.json")
dsl = compiler.generate_spatial_dsl("{case['formula']}", {case['grid'][0]}, {case['grid'][1]})
with open("flow/01_Ideation_Threads/REGRESSION_DSL.json", "w") as f:
    json.dump(dsl, f, indent=4)
""")
        
        s1, _ = run_step("python3 scripts/regression_trigger.py", "Compiling Formula")
        if not s1: continue
        
        # 2. Solver (Dynamic Output)
        res_json = f"flow/03_Output/{cid}_Result.json"
        s2, stdout = run_step(f"python3 scripts/solve_macro_vma.py --ii {case['ii_min']} --dsl flow/01_Ideation_Threads/REGRESSION_DSL.json --output {res_json}", "SMT Modulo Scheduling")
        if not s2: continue
        
        # 3. PseudoGen (Dynamic Report)
        report_txt = f"flow/03_Output/{cid}_PseudoCode.txt"
        s3, _ = run_step(f"python3 scripts/pseudo_gen.py --result {res_json} --report {report_txt}", "Report Generation")
        if not s3: continue
        
        # 4. Reverse Validator (Dynamic Checks)
        s4, _ = run_step(f"python3 scripts/aos_reverse_validator.py {report_txt} flow/01_Ideation_Threads/REGRESSION_DSL.json", "Truth Circle Validation")
        if not s4: continue
        
        passed += 1

    print("\n" + "="*50)
    print(f"📊 SUMMARY: {passed}/{total} Passed")
    if passed == total:
        print("\033[92m🏆 CORE COMPILER STABILITY: CERTIFIED\033[0m")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
