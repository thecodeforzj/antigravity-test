import json
import os
from app.smt_modulo_core import SMTModuloScheduler

class SMTDSLCompiler:
    def __init__(self, manifest_path):
        self.manifest_path = manifest_path
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        self.units = {u['name'].upper(): u for u in self.manifest['hardware']['units']}

    def compile(self, dsl_json):
        """
        Transforms high-level JSON DSL into SMT-compatible instruction and dependency lists.
        dsl_json: List of dicts like {"id": "M1", "op": "FPMUL", "read_bank": 7, "deps": [["PREV", 0]]}
        """
        smt_insts = []
        smt_deps = []
        
        # 1. First Pass: Create instruction objects with hardware-aligned latency
        for d in dsl_json:
            op_name = d['op'].upper()
            if op_name not in self.units:
                raise ValueError(f"Unknown Opcode: {op_name}")
            
            unit_info = self.units[op_name]
            
            inst = {
                "id": d['id'],
                "unit": op_name,
                "latency": unit_info['latency'],
                "loops": d.get("loops", 0),
                "read_bank": d.get("read_bank"),
                "write_bank": d.get("write_bank"),
                "bank_id": d.get("bank_id") # Legacy support
            }
            smt_insts.append(inst)
            
            # 2. Extract dependencies
            # Format: ["target_id", "source_id", "delay_offset"]
            for d_info in d.get("deps", []):
                smt_deps.append((d['id'], d_info[0], d_info[1]))

        # 3. Automatic Optimization: Identifying Bypass (RTOVR)
        # If an instruction has NO explicit write_bank and its result is a dependency,
        # it is inherently treated as a bypass. 
        # (This logic is already handled by our solver because 'write_bank' is None by default)
        
        # 4. Invoke Solver
        scheduler = SMTModuloScheduler(self.manifest_path)
        result = scheduler.solve_optimal_ii(smt_deps, custom_insts=smt_insts)
        
        return result

if __name__ == "__main__":
    # Smoke test: 1-step Horner
    manifest = "flow/02_Specs/Hardware_Manifest.json"
    compiler = SMTDSLCompiler(manifest)
    
    dsl = [
        {"id": "C_LD", "op": "FPMUL", "read_bank": 7}, # Load a9, MUL by x
        {"id": "A_ADD", "op": "FPADD", "read_bank": 7, "deps": [["C_LD", 0]], "write_bank": 7} # Load a8, ADD, STORE
    ]
    
    res = compiler.compile(dsl)
    print(f"Compile Status: {res['status']}, II: {res.get('ii')}")
