import json
import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_dsl_compiler import SMTDSLCompiler
from app.smt_instruction_packer import SMTInstructionPacker

def generate_80_input_vliw_hex():
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest_path)
    packer = SMTInstructionPacker(manifest_path)
    
    print(">>> AOS V5.5 BINARY SAMPLE GENERATOR: 80 Input Saturation Pattern\n")
    
    # 1. 定义 3 阶霍纳向量核 (Loop Body)
    dsl = [
        {"id": "MUL_3", "op": "FPMUL", "read_bank": 7},
        {"id": "ADD_2", "op": "FPADD", "read_bank": 7, "deps": [["MUL_3", 0]]},
        {"id": "MUL_2", "op": "FPMUL", "deps": [["ADD_2", 0]]},
        {"id": "ADD_1", "op": "FPADD", "read_bank": 7, "deps": [["MUL_2", 0]]},
        {"id": "MUL_1", "op": "FPMUL", "deps": [["ADD_1", 0]]},
        {"id": "ADD_0", "op": "FPADD", "read_bank": 7, "write_bank": 7, "deps": [["MUL_1", 0]]}
    ]
    
    # 2. 调用 SMT 寻找最优时序 (II=3)
    print(f"[SMT] Solving core kernel dependencies...")
    result = compiler.compile(dsl)
    
    if result["status"] == "SAT":
        ii = result["ii"]
        print(f"Sub-Kernel SAT: II = {ii}")
        
        # 3. 构造 80 路向量循环 Metadata
        # Scaling: 80 / 4 = 20 batches
        loop_count = 20
        
        print(f"--- FINAL HEX OUTPUT (WITH DLY-AWARE HEADERS) ---")
        
        # 4. 执行 Packer 封包 - 每条指令有独立的 DLY
        for inst in result["instructions"]:
            dly_val = inst.get("dly", 0)
            
            # MSB: VLD[40], LOOPS[29:22], DLY[29:25]... Wait!
            # SDD Layout: bit[MSB-11:MSB-15] = DLY. MSB=40. 40-11=29, 40-15=25.
            # SDD Layout: bit[MSB-22:MSB-29] = LOOPS. MSB=40. 40-22=18, 40-29=11.
            # SDD Layout: bit[MSB-30:MSB-35] = INC. MSB=40. 40-30=10, 40-35=5.
            
            vld_bit = (1 << 40)
            dly_bits = (dly_val & 0x1F) << 25
            loops_bits = (loop_count & 0xFF) << 11
            inc_bits = (ii & 0x3F) << 5
            
            header = vld_bit | dly_bits | loops_bits | inc_bits
            
            print(f"Inst: {inst['id']:<6} | DLY: {dly_val:<2} | Header: 0x{header:011X}")
            
        print("\nNote: Each instruction header now precisely controls its pulsing offset (DLY).")
        
    else:
        print(f"❌ Failed to solve kernel.")

if __name__ == "__main__":
    generate_80_input_vliw_hex()
