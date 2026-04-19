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
        self.instructions = []
        
    def add_instruction(self, inst_id, unit_name, bank_id=None):
        unit_meta = next((u for u in self.manifest["units"] if u["name"] == unit_name), None)
        self.instructions.append({
            "id": inst_id, "unit": unit_name,
            "latency": unit_meta["latency"],
            "t_var": Int(f"t_{inst_id}"),
            "u_idx": Int(f"u_idx_{inst_id}"), 
            "bank_id": bank_id,
            "input_ports": unit_meta.get("input_ports", []),
            "port_map": unit_meta.get("port_map", [])
        })

    def solve_modulo(self, ii, dependencies_list, strict_compact=True):
        opt = Optimize()
        s = opt 
        s.set("timeout", 20000)
        
        # 🟢 AOS 2.3: Integrate Hashes into Metadata
        # (This is returned only on SAT)
        
        for i in self.instructions:
            t, u = i["t_var"], i["u_idx"]
            unit_meta = next(um for um in self.manifest["units"] if um["name"] == i["unit"])
            s.add(t >= 0)
            s.add(u >= 0, u < unit_meta["count"])
            
        for i in self.instructions:
            parents_in_deps = [p_id for c_id, p_id, _ in dependencies_list if c_id == i["id"]]
            if parents_in_deps:
                child_pulse = i["t_var"] - 1
                for p_id in parents_in_deps:
                    parent_obj = next((pi for pi in self.instructions if pi["id"] == p_id), None)
                    if parent_obj:
                        p_ready = parent_obj["t_var"] + parent_obj["latency"]
                        s.add(child_pulse == p_ready)

        for unit_meta in self.manifest["units"]:
            if unit_meta.get("is_pulse"): continue
            relevant = [i for i in self.instructions if i["unit"] == unit_meta["name"]]
            for idx in range(len(relevant)):
                for jdx in range(idx + 1, len(relevant)):
                    i1, i2 = relevant[idx], relevant[jdx]
                    s.add(Implies(i1["t_var"] % ii == i2["t_var"] % ii, i1["u_idx"] != i2["u_idx"]))

        for b_id in range(self.manifest["memory"]["banks"]):
            for m_cycle in range(ii):
                m_ops = [(i["t_var"] % ii == m_cycle, 1) for i in self.instructions if i["bank_id"] == b_id]
                if m_ops: s.add(PbLe(m_ops, 1))

        if strict_compact:
            s.minimize(Sum([i["t_var"] for i in self.instructions]))

        if s.check() == sat:
            model = s.model()
            return {
                "metadata": {
                    "manifest_hash": self.manifest_hash,
                    "model_version": "AOS-2.3-STRICT"
                },
                "ii": ii, 
                "schedule": {i["id"]: model[i["t_var"]].as_long() for i in self.instructions},
                "unit_assignments": {i["id"]: model[i["u_idx"]].as_long() for i in self.instructions}
            }
        return None
