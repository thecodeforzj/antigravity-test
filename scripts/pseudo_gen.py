import json
import os
import sys

# 💠 AOS 3.5 High-Resolution Logic Analyzer & CodeGen
# Generates ASCII Timing Diagrams and Micro-instruction field dumps.

def generate_reports(result_path, manifest_path):
    print(f"🛠️  Analyzing Logic from {os.path.basename(result_path)}...")
    
    with open(result_path, 'r') as f:
        res = json.load(f)
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)["hardware"]
        
    schedule = res["schedule"]
    task_id = res["metadata"].get("spec_dna", "TSK-010")
    dsl_path = f"flow/01_Ideation_Threads/{task_id}_DSL.json"
    
    with open(dsl_path, 'r') as f:
        dsl_data = json.load(f)

    # 1. Expand Activity Timeline
    timeline = {} # t -> {unit_id -> symbol}
    unit_micro_instrs = {} # unit_id -> [fields]
    
    # Track units count to handle indexing (e.g. ur_read_0, ur_read_1)
    unit_counters = {} 
    
    # Sort DSL by id for consistent assignment
    for inst in dsl_data:
        op = inst["op"].upper()
        if op not in unit_counters: unit_counters[op] = 0
        unit_id = f"{op.lower()}_{unit_counters[op]}"
        unit_counters[op] += 1
        
        t_base = schedule.get(inst["id"], 0)
        dly = inst.get("dly", 0)
        loops = inst.get("loops", 0)
        symbol = inst["op"][0] if inst["op"] != "rtovr" else "o"
        
        # Microcode Fields
        unit_meta = next((u for u in manifest["units"] if u["name"].upper() == op), {})
        fields = ["VLD: 1", f"DLY: {dly}", f"LOOPS: {loops}"]
        for f_meta in unit_meta.get("fields", []):
            fname = f_meta["name"].upper()
            fval = inst.get(f_meta["name"], f_meta.get("default", 0))
            fields.append(f"{fname}: {fval}")
        unit_micro_instrs[unit_id] = " | ".join(fields)

        # Timeline
        for k in range(loops + 1):
            t_curr = t_base + dly + k
            if t_curr not in timeline: timeline[t_curr] = {}
            timeline[t_curr][unit_id] = f"{k}{symbol}"

    # 2. Build Timing Diagram
    all_units = sorted(unit_micro_instrs.keys())
    max_t = max(timeline.keys()) if timeline else 0
    header = " Unit         | " + " ".join([f"{t % 10}" if t % 10 == 0 else "." for t in range(max_t + 5)])
    separator = "-" * len(header)
    
    diagram = [header, separator]
    for uid in all_units:
        row = f" {uid:12} |"
        for t in range(max_t + 5):
            cell = timeline.get(t, {}).get(uid, ".")
            row += f" {cell:2}"
        diagram.append(row)
        
    # 3. Build Microcode Report
    microcode = ["💠 AOS 3.5 ACTIVE UNIT MICRO-INSTRUCTION DUMP", "="*60]
    for uid in all_units:
        microcode.append(f"{uid:12}: {unit_micro_instrs[uid]}")

    return "\n".join(diagram) + "\n\n" + "\n".join(microcode)

def main():
    res_path = sys.argv[1] if len(sys.argv) > 1 else "flow/03_Output/TSK-010_Result.json"
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    
    if not os.path.exists(res_path):
        print(f"❌ Result file {res_path} not found.")
        return

    report = generate_reports(res_path, manifest_path)
    output_txt = "flow/03_Output/Add10_PseudoCode.txt"
    with open(output_txt, 'w') as f:
        f.write(report)
    print(f"✅ Visual Logic Analysis saved: {output_txt}")

if __name__ == "__main__":
    main()
