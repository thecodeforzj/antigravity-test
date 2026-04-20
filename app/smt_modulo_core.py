import hashlib
import json
import os
from z3 import *

class SMTModuloScheduler:
    def __init__(self, manifest_path):
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)["hardware"]
        self.instructions = []
        self.unit_vars = {} # inst_id -> u_idx (Z3 Int)
        self.t_vars = {}    # inst_id -> t_start (Z3 Int)
        self.manifest_hash = hashlib.sha256(open(manifest_path, 'rb').read()).hexdigest()
        
    def add_instruction(self, inst_id, unit_name, bank_id=None, **kwargs):
        # 🟢 AOS 3.5: Case-insensitive unit lookup for Real-HW compatibility
        unit_meta = next((u for u in self.manifest["units"] if u["name"].upper() == unit_name.upper()), None)
        if not unit_meta:
            raise KeyError(f"❌ Unit '{unit_name}' not found. Manifest: {[u['name'] for u in self.manifest['units']]}")

        inst_obj = {
            "id": inst_id, 
            "unit": unit_name,
            "latency": unit_meta["latency"],
            "t_var": Int(f"t_{inst_id}"),
            "u_idx": Int(f"u_idx_{inst_id}"), 
            "bank_id": bank_id,
            "input_ports": unit_meta.get("input_ports", []),
            "port_map": unit_meta.get("port_map", []),
            # Defaults for compression fields
            "dly": 0,
            "loops": 0,
            "embed": 0,
            "vld": 1,
            "jump": 0,
            "u_idx_fixed": None
        }
        # Override with kwargs (u_idx_fixed, loops, dly, etc.)
        inst_obj.update(kwargs)
        # Handle special case where u_idx might be passed as u_idx_fixed
        if "u_idx" in kwargs and "u_idx_fixed" not in kwargs:
            inst_obj["u_idx_fixed"] = kwargs["u_idx"]
            
        self.instructions.append(inst_obj)

    def _pre_flight_check(self, ii):
        """🟢 AOS PFC: Prevent Resource Over-saturation"""
        for unit_meta in self.manifest["units"]:
            relevant = [i for i in self.instructions if i["unit"].upper() == unit_meta["name"].upper()]
            required_slots = 0
            for i in relevant:
                # If a unit doesn't support internal loops, it must occupy slots sequentially
                # BUT for PFC we count emission slots. In II=1, we only have 1 emission slot per unit.
                required_slots += 1
            
            if required_slots > unit_meta["count"] * ii:
                return {"safe": False, "reason": f"Unit '{unit_meta['name']}' requires {required_slots} time-slots, but II={ii} only provides {unit_meta['count'] * ii}."}
        return {"safe": True}

    def solve_modulo(self, ii, dependencies_list, strict_compact=True):
        pfc = self._pre_flight_check(ii)
        if not pfc["safe"]:
            return {"status": "UNVERIFIED", "error": f"[PFC_BLOCK] {pfc['reason']}"}
            
        opt = Optimize()
        s = opt 
        s.set("timeout", 20000)
        
        for i in self.instructions:
            t, u = i["t_var"], i["u_idx"]
            unit_meta = next(um for um in self.manifest["units"] if um["name"].upper() == i["unit"].upper())
            s.add(t >= 0)
            
            if i.get("u_idx_fixed") is not None:
                # 🟢 AOS 3.5: Physical Hard-Wiring Compliance
                s.add(u == i["u_idx_fixed"])
            else:
                s.add(u >= 0, u < unit_meta["count"])
            
        for child_id, parent_id, extra_delay in dependencies_list:
            child = next(inst for inst in self.instructions if inst["id"] == child_id)
            parent = next(inst for inst in self.instructions if inst["id"] == parent_id)
            # 🟢 AOS 3.5: DLY-Aware Causality
            s.add(child["t_var"] + child.get("dly", 0) >= 
                  parent["t_var"] + parent.get("dly", 0) + parent["latency"] + extra_delay)

        for unit_meta in self.manifest["units"]:
            # 🟢 AOS 3.5: Macro-Compression Aware Resource Audit
            for m_cycle in range(ii):
                for u_idx_val in range(unit_meta["count"]):
                    m_ops = []
                    for i in self.instructions:
                        if i["unit"].upper() == unit_meta["name"].upper():
                            # Iterations k=0..LOOPS
                            condition = Or([ (i["t_var"] + k) % ii == m_cycle for k in range(i.get("loops", 0) + 1) ])
                            m_ops.append((And(condition, i["u_idx"] == u_idx_val), 1))
                    if m_ops: s.add(PbLe(m_ops, 1))

        # Memory Banks
        bank_count = self.manifest["params"].get("UR_BANK_NUM", 4)
        for b_id in range(bank_count):
            for m_cycle in range(ii):
                m_ops = []
                for i in self.instructions:
                    if i["bank_id"] == b_id:
                        condition = Or([ (i["t_var"] + k) % ii == m_cycle for k in range(i.get("loops", 0) + 1) ])
                        m_ops.append((condition, 1))
                if m_ops: s.add(PbLe(m_ops, 1))

        if strict_compact:
            total_time = Int('total_time')
            s.add(total_time == sum([i["t_var"] for i in self.instructions]))
            opt.minimize(total_time)

        if s.check() == sat:
            m = s.model()
            schedule = {i["id"]: m.eval(i["t_var"]).as_long() for i in self.instructions}
            # Correctly map physical unit assignments
            unit_assignments = {i["id"]: m.eval(i["u_idx"]).as_long() for i in self.instructions}
            
            return {
                "status": "CERTIFIED",
                "ii": ii,
                "schedule": schedule,
                "unit_assignments": unit_assignments,
                "metadata": {
                    "manifest_hash": self.manifest_hash,
                    "model_version": "AOS-3.0-Hrigor",
                    "truth_signature": hashlib.sha256(str(schedule).encode()).hexdigest()
                }
            }
        return None
