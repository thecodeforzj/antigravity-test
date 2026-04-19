import json
import hashlib
from smt_modulo_core import SMTModuloScheduler

class SMTDSLParser:
    def __init__(self, manifest_path):
        self.scheduler = SMTModuloScheduler(manifest_path)
        self.raw_deps = []
        self.dsl_hash = None
    
    def load_instructions(self, dsl_path):
        with open(dsl_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            # 🟢 AOS 2.3: Capture DSL Fingerprint
            self.dsl_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
            data = json.loads(raw_data)
            
        print(f"[PARSER] Loading {len(data)} instructions...")
        for inst in data:
            inst_id = inst["id"]
            op = inst["op"]
            bank = inst.get("bank", None)
            
            if "deps" in inst:
                for parent_info in inst["deps"]:
                    p_id, delay = parent_info[0], parent_info[1]
                    self.raw_deps.append((inst_id, p_id, delay))
                
            self.scheduler.add_instruction(
                inst_id=inst_id,
                unit_name=op,
                bank_id=bank
            )

    def check_integrity(self):
        """🟢 AOS 2.3 Static Sanity Check"""
        # 1. Cycle Detection (DFS)
        visited = set()
        stack = set()
        adj = {}
        for c, p, _ in self.raw_deps:
            if c not in adj: adj[c] = []
            adj[c].append(p)
            
        def has_cycle(v):
            visited.add(v)
            stack.add(v)
            for neighbor in adj.get(v, []):
                if neighbor not in visited:
                    if has_cycle(neighbor): return True
                elif neighbor in stack:
                    return True
            stack.remove(v)
            return False
            
        for node in adj:
            if node not in visited:
                if has_cycle(node):
                    raise ValueError(f"[FATAL-DSL] Circular dependency detected at {node}!")
        
        print("[PARSER] Static Integrity Passed (No Cycles).")
        return True

    def solve_modulo(self, ii):
        self.check_integrity()
        # Pass hashes to meta? No, core does it for manifest. 
        # Parser can add DSL hash here.
        res = self.scheduler.solve_modulo(ii, self.raw_deps, strict_compact=False)
        if res:
            final = self.scheduler.solve_modulo(ii, self.raw_deps, strict_compact=True)
            if final:
                final["metadata"]["dsl_hash"] = self.dsl_hash
            return final
        return None
