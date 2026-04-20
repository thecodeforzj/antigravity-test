import json
import sys
import os
import hashlib

def get_hash(path):
    with open(path, 'r', encoding='utf-8') as f:
        return hashlib.sha256(f.read().encode('utf-8')).hexdigest()

def check_truth(schedule_file, manifest_file, dsl_file, num_iters=10):
    with open(schedule_file, 'r', encoding='utf-8') as f:
        sched = json.load(f)
    
    # 🟢 AOS 2.3: FINGERPRINT VALIDATION
    m_hash_current = get_hash(manifest_file)
    d_hash_current = get_hash(dsl_file)
    
    meta = sched.get("metadata", {})
    if meta.get("manifest_hash") != m_hash_current:
        print("[FAIL-META] HARDWARE MANIFEST MISMATCH! Result is stale.")
        return ["[FAIL-META] Manifest Link Broken"]
    if meta.get("dsl_hash") != d_hash_current:
        print("[FAIL-META] DSL LOGIC MISMATCH! Result is stale.")
        return ["[FAIL-META] DSL Link Broken"]

    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)["hardware"]
    with open(dsl_file, 'r', encoding='utf-8') as f:
        dsl = json.load(f)

    ii = sched["ii"]
    instrs = sched["schedule"]
    units = sched["unit_assignments"]
    
    # ... previous checking logic remains same ...
    meta_info = {i["id"]: {"op": i["op"], "bank": i.get("bank")} for i in dsl}
    latencies = {u["name"]: u["latency"] for u in manifest["units"]}
    
    events = []
    for k in range(num_iters):
        for id, t_base in instrs.items():
            t_abs = t_base + k * ii
            u_name = meta_info[id]["op"]
            u_idx = units.get(id, 0)
            events.append({
                "iter": k, "id": id, "op": u_name, "u_idx": u_idx,
                "t": t_abs, "bank": meta_info[id]["bank"],
                "ready": t_abs + latencies[u_name],
                "pulse": t_abs - 1
            })

    violations = []
    for k in range(num_iters):
        for child_desc in dsl:
            c_id = child_desc["id"]
            if "deps" not in child_desc: continue
            child_ev = next(e for e in events if e["id"] == c_id and e["iter"] == k)
            for p_id, _ in child_desc["deps"]:
                parent_ev = next(e for e in events if e["id"] == p_id and e["iter"] == k)
                if child_ev["pulse"] < parent_ev["ready"]:
                    violations.append(f"[FAIL-SYNC] Iter{k}: {c_id} pulse at {child_ev['pulse']}, but parent {p_id} ready at {parent_ev['ready']}")

    # 🟢 AOS 3.0: High-Rigor Modulo Resource Audit
    for p in range(ii):
        for unit in manifest["units"]:
            u_type = unit["name"]
            u_limit = unit["count"]
            if unit.get("is_pulse"): continue 
            
            # 找到所有在相位 p 占用该类型单元的指令
            # 注意：t_base 是 Result JSON 中的相对启动拍数
            active_in_phase = [inst_id for inst_id, t_base in instrs.items() if (t_base % ii) == p and meta_info[inst_id]["op"] == u_type]
            if len(active_in_phase) > u_limit:
                violations.append(f"[FAIL-MODULO] Phase {p}: {u_type} unit over-saturation! Ops {active_in_phase} compete for {u_limit} slots.")

    # 检查存储库（Bank）冲突（保持绝对时间检查，因为 Bank 通常按拍算）
    time_points = sorted(list(set(e["t"] for e in events)))
    for t in time_points:
        active_banks = [e["bank"] for e in events if e["t"] == t and e["bank"] is not None]
        if len(active_banks) != len(set(active_banks)):
            violations.append(f"[FAIL-BANK] T={t}: Bank collision! {active_banks}")

    return violations

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "flow/03_Output/Taylor3_Result.json"
    manifest = sys.argv[2] if len(sys.argv) > 2 else "flow/02_Specs/Hardware_Manifest.json"
    dsl = sys.argv[3] if len(sys.argv) > 3 else "flow/01_Ideation_Threads/Taylor3_Arr10_DSL.json"
    
    v = check_truth(target, manifest, dsl)
    if not v:
        print("[PASS] PHYSICAL TRUTH SCAN: ALL CLEAR. Schedule is 100% compliant.")
        sys.exit(0)
    else:
        print("[FAIL] PHYSICAL INTEGRITY BREACHED:")
        for err in v[:20]: print(err)
        sys.exit(1)
