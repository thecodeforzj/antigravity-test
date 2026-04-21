import sys
import os
import json

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler

def run_coverage_suite():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS P4.6 DSL GENERALITY & COVERAGE SUITE\n")

    # CASE 1: Diamond Dependency (Convergence)
    #   A (MUL) 
    #  / \
    # B   C (ADD)
    #  \ /
    #   D (MUL)
    diamond_dsl = [
        {"id": "A", "op": "FPMUL", "read_bank": 1},
        {"id": "B", "op": "FPADD", "deps": [["A", 0]]},
        {"id": "C", "op": "FPADD", "deps": [["A", 0]]},
        {"id": "D", "op": "FPMUL", "deps": [["B", 0], ["C", 0]], "write_bank": 2}
    ]

    # CASE 2: High Contention (8 Ops on 4 Ports)
    contention_dsl = []
    for i in range(8):
        contention_dsl.append({"id": f"OP_{i}", "op": "LOGIC", "read_bank": 0})

    # CASE 3: Multi-Bank Interleaving
    interleave_dsl = [
        {"id": "R0", "op": "LOGIC", "read_bank": 0},
        {"id": "R1", "op": "LOGIC", "read_bank": 1},
        {"id": "R2", "op": "LOGIC", "read_bank": 2},
        {"id": "R3", "op": "LOGIC", "read_bank": 3},
        {"id": "R4", "op": "LOGIC", "read_bank": 4},
        {"id": "W0", "op": "LOGIC", "write_bank": 0, "deps": [["R0", 0]]}
    ]

    tests = [
        ("Diamond Dependency", diamond_dsl),
        ("Port Contention (8 on 4)", contention_dsl),
        ("Multi-Bank Interleave", interleave_dsl)
    ]

    for name, dsl in tests:
        print(f"--- TEST: {name} ---")
        try:
            res = compiler.compile(dsl)
            if res["status"] == "SAT":
                print(f"✅ PASS: Best II Found = {res['ii']}")
            else:
                print(f"❌ FAIL: {res.get('reason', 'Unknown Failure')}")
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
        print()

if __name__ == "__main__":
    run_coverage_suite()
