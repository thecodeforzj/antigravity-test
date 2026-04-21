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
        # Override with kwargs
        inst_obj.update(kwargs)
        if "u_idx" in kwargs and "u_idx_fixed" not in kwargs:
            inst_obj["u_idx_fixed"] = kwargs["u_idx"]
            
        self.instructions.append(inst_obj)

    def _pre_flight_check(self, ii):
        """🟢 AOS PFC: Prevent Resource Over-saturation"""
        for unit_meta in self.manifest["units"]:
            relevant = [i for i in self.instructions if i["unit"].upper() == unit_meta["name"].upper()]
            required_slots = len(relevant)
            if required_slots > unit_meta["count"] * ii:
                return {"safe": False, "reason": f"Unit '{unit_meta['name']}' requires {required_slots} slots, but II={ii} only provides {unit_meta['count'] * ii}."}
        return {"safe": True}

    def solve_modulo(self, ii, dependencies_list, strict_compact=True):
        """🟢 AOS P3: Implementation for SDD (FIXED - assert_and_track)"""
        pfc = self._pre_flight_check(ii)
        if not pfc["safe"]:
            return {"status": "UNSAT", "reason": f"PFC_FAIL: {pfc['reason']}"}
            
        s = Solver()
        s.set("timeout", 20000)
        
        # 1. Variables & Constraints mapping from SDD
        for i in self.instructions:
            t, u = i["t_var"], i["u_idx"]
            unit_meta = next(um for um in self.manifest["units"] if um["name"].upper() == i["unit"].upper())
            s.add(t >= 0)
            
            # Use assert_and_track for Unsat Core
            if i.get("u_idx_fixed") is not None:
                s.assert_and_track(u == i["u_idx_fixed"], f"Fixed_Unit_{i['id']}")
            else:
                s.assert_and_track(And(u >= 0, u < unit_meta["count"]), f"Range_Unit_{i['id']}")
            
        # 2. Dependencies
        for idx, (child_id, parent_id, extra_delay) in enumerate(dependencies_list):
            child = next(inst for inst in self.instructions if inst["id"] == child_id)
            parent = next(inst for inst in self.instructions if inst["id"] == parent_id)
            s.assert_and_track(child["t_var"] + child.get("dly", 0) >= 
                  parent["t_var"] + parent.get("dly", 0) + parent["latency"] + extra_delay,
                  f"Dep_{child_id}_{parent_id}")

        # 3. Modulo Resource Constraints (SDD Clause 2.1 + LOOPS Extension)
        for unit_meta in self.manifest["units"]:
            for m_cycle in range(ii):
                for u_idx_val in range(unit_meta["count"]):
                    m_ops = []
                    for i in self.instructions:
                        if i["unit"].upper() == unit_meta["name"].upper():
                            # If LOOPS is present, the instruction occupies multiple cycles
                            loops = i.get("loops", 0)
                            occupancy_conditions = []
                            for offset in range(loops + 1):
                                occupancy_conditions.append((i["t_var"] + offset) % ii == m_cycle)
                            
                            # If ANY of the occupied cycles matches m_cycle
                            condition = Or(*occupancy_conditions)
                            m_ops.append(And(condition, i["u_idx"] == u_idx_val))
                    if len(m_ops) > 1:
                        s.assert_and_track(AtMost(*m_ops, 1), f"ModRes_{unit_meta['name']}_M{m_cycle}_U{u_idx_val}")

        # 4. Bank Access (AX_05 + Multi-Read / Read-Write Conflict)
        bank_count = self.manifest["params"].get("UR_BANK_NUM", 8)
        for b_id in range(bank_count):
            for m_cycle in range(ii):
                read_ops = [] 
                write_ops = []
                for i in self.instructions:
                    loops = i.get("loops", 0)
                    latency = i["latency"]
                    
                    # Determine if this instruction reads from/writes to this bank
                    # bank_id (legacy) counts for both
                    # read_bank/write_bank (new) are explicit
                    is_read = (i.get("bank_id") == b_id) or (i.get("read_bank") == b_id)
                    is_write = (i.get("bank_id") == b_id) or (i.get("write_bank") == b_id)
                    
                    if is_read:
                        for offset in range(loops + 1):
                            read_ops.append((i["t_var"] + offset) % ii == m_cycle)
                    
                    if is_write:
                        for offset in range(loops + 1):
                            write_ops.append((i["t_var"] + latency + 1 + offset) % ii == m_cycle)
                
                if len(write_ops) > 1:
                    s.assert_and_track(AtMost(*write_ops, 1), f"BankWriteConflict_B{b_id}_M{m_cycle}")
                
                if len(read_ops) > 0 and len(write_ops) > 0:
                    # R/W Mutual Exclusion: If any write occurs, no reads allowed
                    for r_idx, r_cond in enumerate(read_ops):
                        for w_idx, w_cond in enumerate(write_ops):
                            s.assert_and_track(Not(And(r_cond, w_cond)), f"BankRWConflict_B{b_id}_M{m_cycle}_R{r_idx}_W{w_idx}")

        # 4.2 Global Port Constraint (System Quotas 4R / 4W)
        for m_cycle in range(ii):
            global_reads = []
            global_writes = []
            for i in self.instructions:
                loops = i.get("loops", 0)
                latency = i["latency"]
                for offset in range(loops + 1):
                    # 128-bit vector = 1 Port Event
                    global_reads.append((i["t_var"] + offset) % ii == m_cycle)
                for offset in range(loops + 1):
                    global_writes.append((i["t_var"] + latency + 1 + offset) % ii == m_cycle)
            
            if len(global_reads) > 4:
                s.assert_and_track(AtMost(*global_reads, 4) , f"GlobalReadLimit_M{m_cycle}")
            if len(global_writes) > 4:
                s.assert_and_track(AtMost(*global_writes, 4), f"GlobalWriteLimit_M{m_cycle}")

        if s.check() == sat:
            m = s.model()
            schedule = {i["id"]: m.eval(i["t_var"]).as_long() for i in self.instructions}
            unit_assignments = {i["id"]: m.eval(i["u_idx"]).as_long() for i in self.instructions}
            return {
                "status": "SAT",
                "ii": ii,
                "schedule": schedule,
                "unit_assignments": unit_assignments
            }
        else:
            try:
                core = s.unsat_core()
                return {"status": "UNSAT", "ii": ii, "unsat_core": [str(c) for c in core]}
            except:
                return {"status": "UNSAT", "ii": ii, "reason": "Conflict detected but Unsat Core unavailable"}

    def solve_optimal_ii(self, dependencies_list, custom_insts=None):
        """🟢 AOS P3: Binary Search II with Theoretical Auditor"""
        if custom_insts:
            self.instructions = custom_insts
        
        # Ensure Z3 variables exist
        for i in self.instructions:
            if "t_var" not in i:
                i["t_var"] = Int(f"t_{i['id']}")
            if "u_idx" not in i:
                i["u_idx"] = Int(f"u_idx_{i['id']}")
            if "latency" not in i:
                unit_meta = next(u for u in self.manifest["units"] if u["name"].upper() == i["unit"].upper())
                i["latency"] = unit_meta["latency"]

        # --- 📈 THEORETICAL AUDIT (ResMII Calculation) ---
        # 1. Compute Unit Bottleneck
        unit_mii = 1
        load_map = {}
        for i in self.instructions:
            load_map[i["unit"]] = load_map.get(i["unit"], 0) + 1
        for unit_name, load in load_map.items():
            unit_meta = next(u for u in self.manifest["units"] if u["name"].upper() == unit_name.upper())
            unit_mii = max(unit_mii, (load + unit_meta["count"] - 1) // unit_meta["count"])
        
        # 2. Global Port Bottleneck (4 Read / 4 Write)
        total_reads = len(self.instructions) # Simplified, should be weighted by operands
        global_read_mii = (total_reads + 3) // 4
        
        # 3. Bank Bottleneck (Single-Port Shared R/W)
        bank_mii = 0
        bank_access_map = {}
        for i in self.instructions:
            for b_key in ["bank_id", "read_bank", "write_bank"]:
                b_val = i.get(b_key)
                if b_val is not None:
                    bank_access_map[b_val] = bank_access_map.get(b_val, 0) + 1
        if bank_access_map:
            bank_mii = max(bank_access_map.values())
            
        theory_min_ii = max(unit_mii, global_read_mii, bank_mii)
        print(f"--- 📊 THEORETICAL AUDIT (MII) ---")
        print(f"   Unit MII: {unit_mii}, Global Port MII: {global_read_mii}, Bank MII: {bank_mii}")
        print(f"   PHYSICAL LIMIT (ResMII): {theory_min_ii}")
        
        ii_min = theory_min_ii
        # 2. Initial range for Binary Search
        ii_max = max(ii_min + 5, sum([i["latency"] for i in self.instructions]) + 10, 32)
        
        best_result = None
        low, high = ii_min, ii_max
        while low <= high:
            mid = (low + high) // 2
            res = self.solve_modulo(mid, dependencies_list)
            # P3 Feedback: Exposing the physical search space
            print(f"   [P3-FEEDBACK] Physical Probe II={mid}... Result: {res['status']}")
            if res["status"] == "SAT":
                best_result = res
                high = mid - 1
            else:
                low = mid + 1
        return best_result or {"status": "FAILED", "reason": "No valid schedule found"}
