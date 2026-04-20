import os
import yaml
import json
import hashlib

# 💠 AOS 3.5 Real HW Spec Synchronizer
# Usage: python3 scripts/hw_spec_sync.py <hw_specs_dir>

def generate_manifest(hw_dir):
    print(f"🔄 Syncing from {hw_dir}...")
    global_path = os.path.join(hw_dir, "global_spec.yaml")
    units_dir = os.path.join(hw_dir, "units")
    
    if not os.path.exists(global_path):
        print(f"❌ Global spec not found: {global_path}")
        return None
        
    with open(global_path, 'r') as f:
        global_cfg = yaml.safe_load(f)
        
    manifest = {
        "metadata": {
            "version": "4.0-REAL",
            "source": hw_dir,
            "architecture": global_cfg.get("architecture")
        },
        "hardware": {
            "params": global_cfg.get("hardware_params", {}),
            "units": []
        }
    }
    
    # Process units
    for unit_file in os.listdir(units_dir):
        if not unit_file.endswith(".yaml"): continue
        with open(os.path.join(units_dir, unit_file), 'r') as f:
            u = yaml.safe_load(f)
            u_name = u.get("name").upper()
            
            # 🟢 AOS 3.5: Dynamic Capacity Mapping
            # For memory units, count is determined by PORTS
            if u_name == "UR_READ":
                count = global_cfg.get("hardware_params", {}).get("UR_READ_PORTS", 1)
            elif u_name == "UR_WRITE":
                count = global_cfg.get("hardware_params", {}).get("UR_WRITE_PORTS", 1)
            elif u_name == "RTOVR":
                count = global_cfg.get("rtovr_fabric", {}).get("total_routers", 8)
            else:
                count = global_cfg.get("hardware_params", {}).get("unit_capacity", {}).get(u_name, 1)

            iq_info = u.get("iq_info", {})
            en_loops = iq_info.get("EN_LOOPS", True) # Default to true for compute

            # Minimal mapping for SMT solver
            manifest["hardware"]["units"].append({
                "name": u_name,
                "latency": u.get("latency", 1),
                "count": count,
                "type": u.get("type", "compute"),
                "en_loops": en_loops,
                "ports_to_rtovr": u.get("ports_to_rtovr", {}),
                "fields": u.get("fields", [])
            })
            
    return manifest

def main():
    hw_dir = "/home/zhangjun/2_code/NPU/aiacc_compiler/aiacc_smt_engine_v2/hw_specs"
    manifest = generate_manifest(hw_dir)
    
    if manifest:
        output_path = "flow/02_Specs/Real_HW_Hardware_Manifest.json"
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"✅ Real HW Manifest generated: {output_path}")
        
        # DNA Mapping for Audit
        dna = f"DNA-Fingerprint: Hardware_Manifest|{hashlib.sha256(open(output_path, 'rb').read()).hexdigest()}"
        print(f"🧬 Fingerprint for Current_Mission.md: \n{dna}")

if __name__ == "__main__":
    main()
