import sys
import os

# Include app directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.smt_instruction_packer import SMTInstructionPacker

def verify_packer_bits():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(">>> AOS P3 Verification Trace: 41-bit High Header Alignment\n")
    
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    packer = SMTInstructionPacker(manifest_path)
    
    # 构造测试用例
    # VLD=1 (bit 127)
    # DLY=15 (bit 116-112)
    test_inst = {
        "unit": "LOGIC",
        "vld": 1,
        "dly": 15,
        "inst_typ": 0
    }
    
    hex_res = packer.pack_instruction(test_inst)
    print(f"[INPUT]  VLD=1, DLY=15")
    print(f"[OUTPUT] Hex: {hex_res}")
    
    # 物理验证 (Hex 拆解)
    # 前 2 个字符代表最高 8 bits [127:120]
    # vld 是最高位，所以第一个字符应该是 0x8 or higher
    first_char = hex_res[0]
    is_vld_ok = (int(first_char, 16) & 0x8) != 0
    
    # DLY 位置验证：DLY 位于 [116:112]
    # 在 128-bit 包中，这属于第 12 到 15 个位。
    # 对应的 Hex 位次应该是第 3 到 4 个字符。
    dly_snip = int(hex_res[2:4], 16)
    # header_val 位移：(DLY & 0x1F) << 25 (相对于 41-bit)
    # 相对于 128-bit，它是 [128-41+25] = 112 位。
    # 简单检查：若 DLY=15 (0x0F)，检查该片段是否包含对应值。
    
    print(f"\n[AUDIT] Checking MSB (VLD bit 127)...")
    if is_vld_ok:
        print("✅ Success: VLD is correctly placed at the MSB.")
    else:
        print(f"❌ Fail: VLD bit not found at MSB. Hex start: {first_char}")

    print(f"\n[AUDIT] Checking DLY Field (bits 116-112)...")
    # 具体的位检查逻辑
    full_int = int(hex_res, 16)
    dly_extracted = (full_int >> 112) & 0x1F
    if dly_extracted == 15:
        print(f"✅ Success: DLY value 15 correctly extracted from bits 116-112.")
    else:
        print(f"❌ Fail: Expected DLY 15, but extracted {dly_extracted}.")

if __name__ == "__main__":
    verify_packer_bits()
