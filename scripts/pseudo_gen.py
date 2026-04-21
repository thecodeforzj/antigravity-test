import json
import os
import sys
import argparse

# 💠 AOS 3.5 Bit-Perfect Phase Analyzer & CodeGen
# Protocol: Unified HEAD (Control) + Unit BODY (Payload)
# Alignment: ports_to_rtovr hard-wiring compliance.

SYM_MAP = {
    "ur_read": "r",
    "ur_write": "w",
    "fpmul": "m",
    "fpadd": "a",
    "rtovr": "o",
    "fptfp": "x",
    "fptint": "i"
}

def generate_reports(result_path, manifest_path):
    print(f"🛠️  Authenticating Physical Truth: {os.path.basename(result_path)}...")
    
    with open(result_path, 'r') as f:
        res = json.load(f)
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)["hardware"]
        
    schedule = res["schedule"]
    unit_assignments = res.get("unit_assignments", {})
    task_id = res["metadata"].get("spec_dna", "TSK-010")
    dsl_path = f"flow/01_Ideation_Threads/{task_id}_DSL.json"
    
    with open(dsl_path, 'r') as f:
        dsl_data = json.load(f)

    timeline = {} # t -> {unit_id -> symbol}
    unit_micro_instrs = {} # unit_id -> list of formatted_strings
    
    ii = res.get("ii", 1)
    for inst in dsl_data:
        op = inst["op"].lower()
        t_base = schedule.get(inst["id"], 0)
        u_idx = unit_assignments.get(inst["id"], 0) 
        unit_id = f"{op}_{u_idx}"
        
        dly = inst.get("dly", 0)
        loops = inst.get("loops", 0)
        inc = inst.get("inc", 0)
        inc_embed = inst.get("inc_embed", 0)
        embed = inst.get("embed", 0)
        embed_end = inst.get("embed_end", 0)
        symbol = SYM_MAP.get(op, "u")
        
        # --- 💠 AOS 3.9: ISA-Aligned IQ Header (Spatial Support) ---
        real_inc = ii if (loops > 0 and embed == 0) else inc
        head = [
            f"VALID:1",             # 1-bit
            f"JUMP:0",              # 1-bit
            f"EMBED:{embed}",       # 3-bit
            f"EMBED_END:{embed_end}",# 6-bit
            f"LOOPS:{loops}",       # 10-bit
            f"COND:0",              # 7-bit
            f"DLY:{dly}",           # 3-bit
            f"INC:{real_inc}",      # 4-bit
            f"INC_EMBED:{inc_embed}" # 6-bit
        ]
        
        # 🟢 BODY: Unit Private Payload
        unit_meta = next((u for u in manifest["units"] if u["name"].lower() == op), {})
        body = []
        reserved = ["vld", "dly", "loops", "inc", "inc_embed"]
        for f_meta in unit_meta.get("fields", []):
            fname = f_meta["name"].lower()
            if fname in reserved: continue
            fval = inst.get(f_meta["name"], f_meta.get("default", 0))
            body.append(f"{fname.upper()}:{fval}")
            
        if unit_id not in unit_micro_instrs: unit_micro_instrs[unit_id] = []
        unit_micro_instrs[unit_id].append(f"HEAD:[{'|'.join(head)}] | BODY:[{'|'.join(body)}]")

        # Timeline Expansion
        for k in range(loops + 1):
            # 🟢 AOS 3.7: Visual Interleaving (Stride = II)
            t_curr = t_base + dly + k * ii
            if t_curr not in timeline: timeline[t_curr] = {}
            timeline[t_curr][unit_id] = f"{k % 10}{symbol}"

    # 2. Build Timing Diagram
    active_ids = set()
    for t_data in timeline.values():
        active_ids.update(t_data.keys())

    # Industry Standard Base Set
    base_units = [
        "fpadd_0", "fpmul_0", 
        "ur_read_0", "ur_read_1", "ur_read_2", "ur_read_3",
        "ur_write_0", "ur_write_1", "ur_write_2", "ur_write_3",
        "rtovr_0", "rtovr_1", "rtovr_2", "rtovr_3", "rtovr_4", "rtovr_5", "rtovr_6", "rtovr_7"
    ]
    
    display_units = []
    seen = set()
    for uid in base_units:
        display_units.append(uid)
        seen.add(uid)
    for uid in sorted(active_ids):
        if uid not in seen:
            display_units.append(uid)
    
    max_t = max(timeline.keys()) if timeline else 0
    header = " Unit         | " + " ".join([f"{t % 10}" if t % 10 == 0 else " ." for t in range(max_t + 5)])
    separator = "-" * len(header)
    
    diagram = [header, separator]
    for uid in display_units:
        row = f" {uid:12} |"
        for t in range(max_t + 5):
            cell = timeline.get(t, {}).get(uid, ".")
            row += f" {cell:2}"
        diagram.append(row)
        
    # 3. Build Microcode Report
    microcode = ["💠 AOS 3.5 TRUTH-ALIGNED MICRO-INSTRUCTION DUMP", "="*60]
    for uid in sorted(unit_micro_instrs.keys()):
        for idx, mcode in enumerate(unit_micro_instrs[uid]):
            tag = f"{uid}[{idx}]" if len(unit_micro_instrs[uid]) > 1 else uid
            microcode.append(f"{tag:12}: {mcode}")

    return "\n".join(diagram) + "\n\n" + "\n".join(microcode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=str, default="flow/03_Output/TSK-010_Result.json")
    parser.add_argument("--report", type=str, default="flow/03_Output/Add10_PseudoCode.txt")
    args = parser.parse_args()
    
    res_path = args.result
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    
    if not os.path.exists(res_path):
        print(f"❌ Result file {res_path} not found.")
        return

    report = generate_reports(res_path, manifest_path)
    output_txt = args.report
    with open(output_txt, 'w') as f:
        f.write(report)
    print(f"✅ Truth-Aligned Analysis Output: {output_txt}")

if __name__ == "__main__":
    main()
