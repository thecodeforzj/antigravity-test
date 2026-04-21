import json

class SMTVisualizer:
    def __init__(self, manifest_path):
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)["hardware"]
        self.units_meta = {u["name"].upper(): u for u in self.manifest["units"]}

    def generate_horizontal_timing(self, schedule, instructions, ii, max_cycles=20):
        """
        Creates an ASCII horizontal timing diagram.
        X-axis: Cycles
        Y-axis: Hardware Units / RTOVRs
        """
        # 1. Identify all physical instances to track
        rows = []
        # Compute units
        for u_name in ["FPADD", "FPMUL", "LOGIC"]:
            count = self.units_meta.get(u_name, {}).get("count", 0)
            for i in range(count):
                rows.append({"label": f"{u_name.lower()}_{i}", "type": "UNIT", "name": u_name, "idx": i})
        
        # Memory units
        for u_name in ["UR_READ", "UR_WRITE"]:
            count = self.units_meta.get(u_name, {}).get("count", 0)
            for i in range(count):
                rows.append({"label": f"{u_name.lower()}_{i}", "type": "UNIT", "name": u_name, "idx": i})
        
        # RTOVRs (0-7 for inputs, 30-33 for UR_READ outputs)
        for i in [3, 4, 5, 6, 30, 31, 32, 33]:
            rows.append({"label": f"rtovr_{i}", "type": "RTOVR", "idx": i})

        # 2. Populate the grid
        grid = [[" . " for _ in range(max_cycles)] for _ in rows]
        
        for inst in instructions:
            inst_id = inst["id"]
            if inst_id not in schedule: continue
            
            t_start = schedule[inst_id]
            u_idx = inst.get("u_idx", 0)
            u_name = inst["unit"].upper()
            latency = inst.get("latency", 1)
            
            # Labeling parts
            parts = inst_id.split('_')
            op_map = {"FPADD": "A", "FPMUL": "M", "UR_READ": "R", "UR_WRITE": "W", "LOGIC": "L"}
            prefix = op_map.get(u_name, u_name[0].upper())
            suffix = parts[-1] if len(parts) > 1 else ""
            display_label = (prefix + suffix)[:3].center(3)

            # --- Row Population Logic ---
            for r_idx, row in enumerate(rows):
                # 1. Main Unit row
                if row["type"] == "UNIT" and row["name"] == u_name and row["idx"] == u_idx:
                    if t_start < max_cycles:
                        grid[r_idx][t_start] = display_label
                
                # 2. RTOVR row (Physical Trace)
                if row["type"] == "RTOVR":
                    r_idx_val = row["idx"]
                    unit_meta = self.units_meta.get(u_name, {})
                    ports = unit_meta.get("ports_to_rtovr", {})
                    
                    # Compute Input Mapping: Uses RTOVR during issue cycle T
                    for p_name, p_info in ports.items():
                        target = p_info.get("target_rtovr")
                        if target == f"rtovr_{r_idx_val}":
                            if t_start < max_cycles:
                                grid[r_idx][t_start] = display_label

                    # Read Output Mapping: Data appears on RTOVR at T + 1
                    if u_name == "UR_READ":
                        # Manifest maps UR_RDATA_k to specific sel_index
                        port_key = f"UR_RDATA_{u_idx}"
                        if port_key in ports:
                            sel_index = ports[port_key].get("sel_index")
                            if sel_index == r_idx_val:
                                t_ready = t_start + 1
                                if t_ready < max_cycles:
                                    grid[r_idx][t_ready] = display_label

        # 3. Format output
        header = " Unit         | " + "".join([f"{c:<3}" if c % 5 == 0 else " . " for c in range(max_cycles)])
        separator = "-" * len(header)
        
        output = [header, separator]
        for r_idx, row in enumerate(rows):
            line = f" {row['label']:<12} | " + "".join(grid[r_idx])
            output.append(line)
            
        return "\n".join(output)

    def generate_pipelined_trace(self, schedule, instructions, ii, num_iters=10, max_cycles=64):
        """
        🟢 AOS V4.1: Industrial Multi-Iter Horizontal Timeline
        Matches the user's requested high-density ASCII format.
        """
        rows = []
        for u_name in ["FPADD", "FPMUL"]:
            count = self.units_meta.get(u_name, {}).get("count", 0)
            for i in range(count):
                rows.append({"label": f"{u_name.lower()}_{i}", "type": "UNIT", "name": u_name, "idx": i})
        for u_name in ["UR_READ", "UR_WRITE"]:
            count = self.units_meta.get(u_name, {}).get("count", 0)
            for i in range(count):
                rows.append({"label": f"{u_name.lower()}_{i}", "type": "UNIT", "name": u_name, "idx": i})
        for i in range(8):
            rows.append({"label": f"rtovr_{i}", "type": "RTOVR", "idx": i})

        # Initialize grid with 3-char cells
        grid = [[" . " for _ in range(max_cycles)] for _ in rows]
        
        op_map = {"FPADD": "a", "FPMUL": "m", "UR_READ": "r", "UR_WRITE": "w"}

        for it in range(num_iters):
             offset = it * ii
             for inst in instructions:
                inst_id = inst["id"]
                if inst_id not in schedule: continue
                
                t_base = schedule[inst_id]
                t_start = t_base + offset
                if t_start >= max_cycles: continue
                
                u_idx = inst.get("u_idx", 0)
                u_name = inst["unit"].upper()
                latency = inst.get("latency", 1)
                
                # Label: IterIndex + OpChar (e.g. 0a)
                op_char = op_map.get(u_name, u_name[0].lower())
                display_label = f"{it}{op_char}"
                if len(display_label) == 2: display_label = display_label + " "
                if len(display_label) > 3: display_label = display_label[:3]

                for r_idx, row in enumerate(rows):
                    # 1. Physical Unit Rows
                    if row["type"] == "UNIT" and row["name"] == u_name and row["idx"] == u_idx:
                        # Handle potential overlap in visual (though hardware forbids it)
                        if grid[r_idx][t_start] == " . ":
                            grid[r_idx][t_start] = display_label
                        else:
                            # If already occupied (shouldn't happen with correct II), append
                            grid[r_idx][t_start] = (grid[r_idx][t_start].strip() + display_label.strip()).center(3)
                    
                    # 2. RTOVR Rows (using 'o' suffix per user sample)
                    if row["type"] == "RTOVR":
                        ports = self.units_meta.get(u_name, {}).get("ports_to_rtovr", {})
                        r_label = f"{it}o "
                        # Inputs at T-1 (Routing/Setup cycle)
                        for p_name, p_info in ports.items():
                             if p_info.get("target_rtovr") == f"rtovr_{row['idx']}":
                                 t_setup = t_start - 1
                                 if t_setup >= 0 and t_setup < max_cycles:
                                     if grid[r_idx][t_setup] == " . ":
                                         grid[r_idx][t_setup] = r_label
                                     else:
                                         grid[r_idx][t_setup] = (grid[r_idx][t_setup].strip() + r_label.strip()).center(3)
                        # Read Output at T+1
                        if u_name == "UR_READ":
                            port_key = f"UR_RDATA_{u_idx}"
                            if port_key in ports and ports[port_key].get("sel_index") == row["idx"]:
                                if t_start + 1 < max_cycles:
                                     if grid[r_idx][t_start+1] == " . ":
                                         grid[r_idx][t_start+1] = r_label
                                     else:
                                         grid[r_idx][t_start+1] = (grid[r_idx][t_start+1].strip() + r_label.strip()).center(3)

        # 3. Formatting
        title = f"Multi-Iter Horizontal Timeline (N={num_iters}, II={ii}, total_T={max_cycles})"
        # X-Axis: 0 . . . . . . . . . 0
        x_axis = " Unit         | "
        for c in range(max_cycles):
            if c % 10 == 0:
                x_axis += f"{c//10 % 10:<3}"
            else:
                x_axis += " . "
        
        separator = "-" * len(x_axis)
        output = [title, x_axis, separator]
        
        for r_idx, row in enumerate(rows):
            line = f"{row['label']:<13}|" + "".join(grid[r_idx])
            output.append(line)
            
        return "\n".join(output)
