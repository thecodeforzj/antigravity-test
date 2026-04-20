import json
import hashlib
from z3 import *

class SMTModuloScheduler:
    def __init__(self, manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            # 🟢 AOS 2.3: Capture Manifest Fingerprint
            self.manifest_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
            data = json.loads(raw_data)
            self.manifest = data["hardware"]
            self.model_meta = data.get("model_meta", {})
        self.instructions = []
        
    def add_instruction(self, inst_id, unit_name, bank_id=None, **kwargs):
        # 🟢 AOS 3.5: Case-insensitive unit lookup for Real-HW compatibility
        unit_meta = next((u for u in self.manifest["units"] if u["name"].upper() == unit_name.upper()), None)
        if not unit_meta:
            raise KeyError(f"❌ Unit '{unit_name}' not found. Manifest: {[u['name'] for u in self.manifest['units']]}")

        self.instructions.append({
            "id": inst_id, "unit": unit_name,
            "latency": unit_meta["latency"],
            "t_var": Int(f"t_{inst_id}"),
            "u_idx": Int(f"u_idx_{inst_id}"), 
            "bank_id": bank_id,
            "input_ports": unit_meta.get("input_ports", []),
            "port_map": unit_meta.get("port_map", []),
            # 💠 AOS 3.5: Extended Compression Fields
            "dly": kwargs.get("dly", 0),
            "loops": kwargs.get("loops", 0),
            "embed": kwargs.get("embed", 0),
            "vld": kwargs.get("vld", 1),
            "jump": kwargs.get("jump", 0)
        })
    def _pre_flight_check(self, ii):
        """🟢 AOS 2.6: Generic Resource Density Audit"""
        for unit_meta in self.manifest["units"]:
            # AOS 3.0: 包含脉冲单元的强度校核
            needed = len([i for i in self.instructions if i["unit"].upper() == unit_meta["name"].upper()])
            capacity = unit_meta["count"] * ii
            if needed > capacity:
                return {
                    "safe": False,
                    "reason": f"Resource Over-saturation: Unit '{unit_meta['name']}' requires {needed} time-slots, but II={ii} only provides {capacity}."
                }
        return {"safe": True}

    def solve_modulo(self, ii, dependencies_list, strict_compact=True):
        # 🟢 AOS 2.6: Mandatory PFC Check before SMT Heavy-Lift
        pfc = self._pre_flight_check(ii)
        if not pfc["safe"]:
            return {"status": "UNVERIFIED", "error": f"[PFC_BLOCK] {pfc['reason']}"}
            
        opt = Optimize()
        s = opt 
        s.set("timeout", 20000)
        
        # 🟢 AOS 2.3: Integrate Hashes into Metadata
        # (This is returned only on SAT)
        
        for i in self.instructions:
            t, u = i["t_var"], i["u_idx"]
            unit_meta = next(um for um in self.manifest["units"] if um["name"].upper() == i["unit"].upper())
            s.add(t >= 0)
            s.add(u >= 0, u < unit_meta["count"])
            
        for i in self.instructions:
            # Find all (parent_id, extra_delay) for this child
            parents = [(p_id, d) for c_id, p_id, d in dependencies_list if c_id == i["id"]]
            for p_id, d in parents:
                parent_obj = next((pi for pi in self.instructions if pi["id"] == p_id), None)
                if parent_obj:
                    # 🟢 AOS 3.5: DLY-Aware Dependency Chain
                    s.add(i["t_var"] + i["dly"] >= parent_obj["t_var"] + parent_obj["dly"] + parent_obj["latency"] + d + 1)

        for unit_meta in self.manifest["units"]:
            # AOS 3.0: 脉冲单元同样受到硬件并行度限制 (count 约束)
            relevant = [i for i in self.instructions if i["unit"].upper() == unit_meta["name"].upper()]
            for idx in range(len(relevant)):
                for jdx in range(idx + 1, len(relevant)):
                    i1, i2 = relevant[idx], relevant[jdx]
                    # 🟢 AOS 3.5: Cyclic Expansion for LOOPS
                    # If any of the expanded cycles of i1 conflicts with i2's expanded cycles
                    for k1 in range(i1["loops"] + 1):
                        for k2 in range(i2["loops"] + 1):
                            s.add(Implies((i1["t_var"] + k1) % ii == (i2["t_var"] + k2) % ii, i1["u_idx"] != i2["u_idx"]))

        # 🟢 AOS 3.5: Support Real-HW param 'UR_BANK_NUM'
        bank_count = self.manifest["params"].get("UR_BANK_NUM", 4)
        for b_id in range(bank_count):
            for m_cycle in range(ii):
                # 🟢 AOS 3.5: Bank Occupancy also expanded by LOOPS
                m_ops = []
                for i in self.instructions:
                    if i["bank_id"] == b_id:
                        for k in range(i["loops"] + 1):
                            m_ops.append(((i["t_var"] + k) % ii == m_cycle, 1))
                if m_ops: s.add(PbLe(m_ops, 1))

        if strict_compact:
            s.minimize(Sum([i["t_var"] for i in self.instructions]))

        if s.check() == sat:
            model = s.model()
            # 🟢 AOS 3.0: 确保所有指令（含脉冲型）都在生成的 Schedule 中
            schedule = {}
            unit_assignments = {}
            for i in self.instructions:
                val = model[i["t_var"]]
                schedule[i["id"]] = val.as_long() if val is not None else 0
                u_val = model[i["u_idx"]]
                unit_assignments[i["id"]] = u_val.as_long() if u_val is not None else 0

            # 生成增强型 Work-Product Signature
            content_fingerprint = hashlib.sha256(json.dumps(schedule, sort_keys=True).encode()).hexdigest()
            
            return {
                "metadata": {
                    "manifest_hash": self.manifest_hash,
                    "spec_dna": self.model_meta.get("task_id", "TSK-004"),
                    "model_version": "AOS-3.0-Hrigor",
                    "truth_signature": content_fingerprint
                },
                "ii": ii, 
                "schedule": schedule,
                "unit_assignments": unit_assignments,
                "status": "CERTIFIED"
            }
        return {"status": "UNVERIFIED", "error": "No SAT solution found"}
