import json
import os
from app.smt_modulo_core import SMTModuloScheduler
from app.smt_visualizer import SMTVisualizer

class SMTDSLCompiler:
    def __init__(self, manifest_path):
        self.manifest_path = manifest_path
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        self.units = {u['name'].upper(): u for u in self.manifest['hardware']['units']}
        self.visualizer = SMTVisualizer(manifest_path)

    def _parse_dsl(self, dsl_json):
        """
        Internal helper to convert JSON DSL to SMT data structures.
        AOS V4.1: Decoupling Fused Reads (AX_07 Enforcement)
        """
        smt_insts = []
        smt_deps = []
        for d in dsl_json:
            op_name = d['op'].upper()
            if op_name not in self.units:
                raise ValueError(f"Unknown Opcode: {op_name}")
            unit_info = self.units[op_name]
            
            # --- 1. Handle Implicit Reads (Lower as dedicated UR_READ) ---
            compute_inst_id = d['id']
            if d.get("read_bank") is not None:
                read_inst_id = f"R_{compute_inst_id}"
                smt_insts.append({
                    "id": read_inst_id,
                    "unit": "UR_READ",
                    "latency": self.units["UR_READ"]["latency"],
                    "read_bank": d["read_bank"]
                })
                # compute depends on read (AX_07: UR_READ latency = 1)
                smt_deps.append((compute_inst_id, read_inst_id, 0)) 

            # --- 2. Main Compute Instruction ---
            inst = {
                "id": compute_inst_id,
                "unit": op_name,
                "latency": unit_info['latency'],
                "write_bank": d.get("write_bank"),
                "bank_id": d.get("bank_id")
            }
            smt_insts.append(inst)
            
            # --- 3. Dependencies ---
            for d_info in d.get("deps", []):
                parent_id, extra = d_info
                # If parent was a fused read, we already depend on its compute part
                smt_deps.append((d['id'], parent_id, extra))
                
        return smt_insts, smt_deps

    def compile(self, dsl_input):
        """
        🟢 AOS V5.0: Universal Scale-Agnostic Compiler
        Supports arbitrary DSL + arbitrary inputs via metadata.
        """
        if isinstance(dsl_input, dict) and "instructions" in dsl_input:
            meta = dsl_input.get("metadata", {})
            instructions = dsl_input["instructions"]
        else:
            meta = {}
            instructions = dsl_input

        # 1. Generate SMT instructions
        smt_insts, smt_deps = self._parse_dsl(instructions)
        
        # 2. Invoke SMT Solver
        scheduler = SMTModuloScheduler(self.manifest_path)
        result = scheduler.solve_optimal_ii(smt_deps, custom_insts=smt_insts)
        
        # 3. Apply Scaling Generality (AX_09)
        if result["status"] == "SAT":
            ii = result["ii"]
            total_inputs = meta.get("total_inputs", 1)
            vec_width = meta.get("vector_width", 4)
            
            # --- 🛠️ DLY FIELD BACKFILL ---
            # Extract t_start and unit assignments from SMT result
            for inst in smt_insts:
                inst_id = inst["id"]
                if inst_id in result["schedule"]:
                    inst["dly"] = result["schedule"][inst_id]
                if inst_id in result.get("unit_assignments", {}):
                    inst["u_idx"] = result["unit_assignments"][inst_id]
            result["instructions"] = smt_insts # Attach updated inst list

            # Map parameters to VLIW Header logic
            if total_inputs > 1:
                loop_count = (total_inputs + vec_width - 1) // vec_width
                result["header"] = {
                    "INC": ii,
                    "LOOPS": loop_count,
                    "VLD": 1
                }
                # Verification print
                # print(f"[GENERALITY] Scale: {total_inputs} in -> {loop_count} iterations @ INC={ii}")
            else:
                result["header"] = {"INC": ii, "LOOPS": 1, "VLD": 1}
            
            # --- 📊 GENERATE VISUALIZATION ---
            viz_str = self.visualizer.generate_horizontal_timing(result["schedule"], result["instructions"], ii, max_cycles=40)
            result["visual"] = viz_str
            print("\n--- HORIZONTAL TIMING DIAGRAM ---")
            print(viz_str)
            print("---------------------------------\n")
        
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
