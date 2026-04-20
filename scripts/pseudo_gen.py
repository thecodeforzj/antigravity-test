import json
import os
import sys

# 💠 AOS 3.5 Pseudo-Instruction CodeGen Engine
# Maps SMT results back to hardware bitfields

def generate_pseudo_code(result_path, manifest_path):
    print(f"🛠️  Generating Pseudo Code from {os.path.basename(result_path)}...")
    
    with open(result_path, 'r') as f:
        res = json.load(f)
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)["hardware"]
        
    schedule = res["schedule"]
    # We need access to the original DSL to get compression fields (loops, dly, etc.)
    # In a real pipeline, we'd pass the full inst objects.
    # For now, we'll try to find the DSL based on naming.
    task_id = res["metadata"].get("spec_dna", "TSK-010")
    dsl_path = f"flow/01_Ideation_Threads/{task_id}_DSL.json"
    
    with open(dsl_path, 'r') as f:
        dsl_data = json.load(f)

    # 1. Expand all instruction instances across time
    timeline = {} # cycle -> {unit_name -> [fields]}
    
    for inst in dsl_data:
        inst_id = inst["id"]
        t_base = schedule.get(inst_id, 0)
        u_name = inst["op"].upper()
        loops = inst.get("loops", 0)
        
        # Get Unit Fields from Manifest
        unit_meta = next((u for u in manifest["units"] if u["name"].upper() == u_name), {})
        private_fields = unit_meta.get("fields", [])
        
        # Common Header Fields (Mocked for Demo based on spec)
        common_fields = [
            ("VALID", 1),
            ("JUMP", inst.get("jump", 0)),
            ("EMBED", inst.get("embed", 0)),
            ("EMBED_END", inst.get("embed_end", 0)),
            ("LOOPS", loops),
            ("COND", inst.get("cond", 0)),
            ("DLY", inst.get("dly", 0)),
            ("INC", inst.get("inc", 0)),
            ("INC_EMBED", inst.get("inc_embed", 0))
        ]
        
        dly = inst.get("dly", 0)
        for k in range(loops + 1):
            t_curr = t_base + dly + k
            if t_curr not in timeline: timeline[t_curr] = {}
            if u_name not in timeline[t_curr]: timeline[t_curr][u_name] = []
            
            # Record Instruction State
            line = []
            # Add Common
            for f, v in common_fields:
                line.append(f"{f}: {v}")
            # Add Private
            for f_meta in private_fields:
                f_name = f_meta["name"]
                f_val = inst.get(f_name, f_meta.get("default", 0))
                line.append(f"{f_name.upper()}: {f_val}")
            
            timeline[t_curr][u_name].append(" | ".join(line))

    # 2. Output Formatting
    output_lines = ["💠 AOS 3.5 PSEUDO-INSTRUCTION AUTOMATIC GENERATION REPORT", "="*60 + "\n"]
    for t in sorted(timeline.keys()):
        output_lines.append(f"Cycle {t:03}:")
        for unit, insts in timeline[t].items():
            for s in insts:
                output_lines.append(f"  [{unit:10}] {s}")
        output_lines.append("-" * 60)
        
    return "\n".join(output_lines)

def main():
    res_path = sys.argv[1] if len(sys.argv) > 1 else "flow/03_Output/TSK-010_Result.json"
    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    
    if not os.path.exists(res_path):
        print("❌ Result file not found. Please run solver first.")
        return

    report = generate_pseudo_code(res_path, manifest_path)
    output_txt = "flow/03_Output/Add10_PseudoCode.txt"
    with open(output_txt, 'w') as f:
        f.write(report)
    print(f"✅ PseudoCode report saved: {output_txt}")

if __name__ == "__main__":
    main()
