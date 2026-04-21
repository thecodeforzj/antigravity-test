import os
import json
from app.smt_modulo_core import SMTModuloScheduler
from app.smt_instruction_packer import SMTInstructionPacker

class SMTCompiler:
    def __init__(self, manifest_path):
        self.scheduler = SMTModuloScheduler(manifest_path)
        self.packer = SMTInstructionPacker(manifest_path)
        self.manifest_path = manifest_path

    def compile_kernel(self, instructions_def, dependencies):
        """🟢 AOS P3.1: Incremental Linkage (Solver + Packer)"""
        print(f">>> Compiling Kernel with {len(instructions_def)} ops...")
        
        # 1. Load instructions into scheduler
        for inst in instructions_def:
            self.scheduler.add_instruction(
                inst_id=inst["id"],
                unit_name=inst["unit"],
                bank_id=inst.get("bank_id"),
                **inst.get("params", {})
            )
            
        # 2. Solve Optimal II
        result = self.scheduler.solve_optimal_ii(dependencies)
        if result["status"] != "SAT":
            return {"status": "FAILED", "reason": result.get("reason", "UNSAT")}
            
        # 3. Pack to Binary Hex - Incremental P3.3: Parallel Aggregation
        ii = result["ii"]
        schedule = result["schedule"]
        unit_assignments = result["unit_assignments"]
        
        # Group by time T
        time_groups = {}
        for i_id, t in schedule.items():
            if t not in time_groups: time_groups[t] = []
            time_groups[t].append(i_id)
            
        sorted_times = sorted(time_groups.keys())
        hex_output = []
        
        for t in sorted_times:
            ids_in_slot = time_groups[t]
            # Check AX_03: Shared INC
            common_inc = None
            for idx, i_id in enumerate(ids_in_slot):
                inst_obj = next(i for i in self.scheduler.instructions if i["id"] == i_id)
                curr_inc = inst_obj.get("inc", 0)
                if idx == 0: common_inc = curr_inc
                elif common_inc != curr_inc:
                    raise ValueError(f"❌ AX_03 Violation at T={t}: Incompatible INC strides ({common_inc} vs {curr_inc}) in same VLIW.")

            # Construct parallel pack data
            pack_data = {
                "vld": 1,
                "t": t,
                "inc": common_inc,
                "loops": next(i for i in self.scheduler.instructions if i["id"] == ids_in_slot[0]).get("loops", 0)
            }
            
            # Merging Units into one Packet
            # This is a simplified merge: in reality, each unit has its own bitfield
            # Packer will handle the 'CODE' field concatenation based on active units
            # For P3.3, we'll demonstrate by passing a list of active units
            final_hex = self.packer.pack_instruction_parallel(ids_in_slot, self.scheduler.instructions, pack_data)
            hex_output.append({"t": t, "hex": final_hex, "ids": ids_in_slot})
            
        # 4. Generate Detailed Physical Timing Trace (The Logical Evidence)
        # We unroll loops and include RTOVR pulse timing
        trace = {}
        for t_start in sorted_times:
            ids_in_slot = time_groups[t_start]
            loops = next(i for i in self.scheduler.instructions if i["id"] == ids_in_slot[0]).get("loops", 0)
            
            # Parallel Pulsing: All units in ids_in_slot start at t_start
            for l_cnt in range(loops + 1):
                cycle = t_start + l_cnt
                if cycle not in trace: trace[cycle] = {"units": {}, "rtovr": {}}
                
                for i_id in ids_in_slot:
                    inst_obj = next(i for i in self.scheduler.instructions if i["id"] == i_id)
                    unit_name = inst_obj["unit"]
                    trace[cycle]["units"].setdefault(unit_name, []).append(f"{i_id}[#{l_cnt}]")
                    
                    # AX_05: Map Bank Read/Write events
                    bank_id = inst_obj.get("bank_id")
                    if bank_id is not None:
                        # READ at Cycle T
                        trace[cycle]["units"].setdefault(f"BANK_{bank_id}_RD", []).append(f"READ_{i_id}")
                        # WRITE at Cycle T + Latency + 1
                        w_cycle = cycle + inst_obj["latency"] + 1
                        if w_cycle not in trace: trace[w_cycle] = {"units": {}, "rtovr": {}}
                        trace[w_cycle]["units"].setdefault(f"BANK_{bank_id}_WR", []).append(f"WRITE_{i_id}")
                    
                    # Deduce RTOVR pulse from Sync Protocol (T+1)
                    trace[cycle + 1] = trace.get(cycle + 1, {"units": {}, "rtovr": {}})
                    trace[cycle + 1]["rtovr"][f"rtovr_for_{i_id}"] = "PULSE_ACTIVE"

        return {
            "status": "SUCCESS",
            "ii": ii,
            "binary": hex_output,
            "logical_trace": trace
        }

    def print_timing_report(self, result):
        """🟢 AOS Milestone: Human-Readable Timing Proof"""
        trace = result["logical_trace"]
        sorted_cycles = sorted(trace.keys())
        
        print("\n--- 🏟️ SMT LOGICAL TIMING REPORT (Stage 1 Audit) ---")
        print(f"{'Cycle':<8} | {'Active Units':<30} | {'RTOVR Pulsing'}")
        print("-" * 60)
        
        for c in sorted_cycles:
            units = ", ".join([f"{k}:{v}" for k, v in trace[c].get("units", {}).items()])
            rtovr = ", ".join(trace[c].get("rtovr", {}).keys())
            print(f"{c:<8} | {units:<30} | {rtovr}")
        print("-" * 60)

if __name__ == "__main__":
    # Smoke test for linkage
    compiler = SMTCompiler("flow/02_Specs/Hardware_Manifest.json")
    insts = [
        {"id": "ADD0", "unit": "FPADD"},
        {"id": "MUL0", "unit": "FPMUL"}
    ]
    deps = [("MUL0", "ADD0", 0)]
    
    output = compiler.compile_kernel(insts, deps)
    print(json.dumps(output, indent=2))
