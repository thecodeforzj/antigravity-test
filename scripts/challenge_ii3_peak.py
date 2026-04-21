import json
import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler
from app.smt_instruction_packer import SMTInstructionPacker

def generate_ii3_horner_hex():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    
    print(">>> AOS V5.6 PERFORMANCE PEAK: Challenging II=3 via Bank-Distro\n")
    
    # 强制常数分摊到 Bank 7 和 Bank 6，消除访存瓶颈
    # 结果回写到 Bank 0
    dsl = [
        {"id": "MUL_3", "op": "FPMUL", "read_bank": 7},         # a3 in Bank 7
        {"id": "ADD_2", "op": "FPADD", "read_bank": 7, "deps": [["MUL_3", 0]]}, # a2 in Bank 7
        {"id": "MUL_2", "op": "FPMUL", "deps": [["ADD_2", 0]]},
        {"id": "ADD_1", "op": "FPADD", "read_bank": 6, "deps": [["MUL_2", 0]]}, # a1 in Bank 6
        {"id": "MUL_1", "op": "FPMUL", "deps": [["ADD_1", 0]]},
        {"id": "ADD_0", "op": "FPADD", "read_bank": 6, "write_bank": 0, "deps": [["MUL_1", 0]]} # a0 in Bank 6, Result in Bank 0
    ]
    
    print(f"[RUN] SMT Performance Audit for Optimized Kernel...")
    result = compiler.compile(dsl)
    
    if result["status"] == "SAT":
        ii = result["ii"]
        print(f"--- PERFORMANCE ACHIEVED ---")
        print(f"   Final II = {ii} (Matches Compute Limit!)")
        
        # 封装 Header
        loop_count = 20
        # Header (LOOPS=20, INC=3)
        # INC = 3 << 11, LOOPS = 20 << 17
        header = (1 << 40) | (20 << 17) | (ii << 11)
        
        print(f"Header for II=3: {hex(header).upper()}")
    else:
        print(f"FAILED to reach II=3. Status: {result.get('status')}")

if __name__ == "__main__":
    generate_ii3_horner_hex()
