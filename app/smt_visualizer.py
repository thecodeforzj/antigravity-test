class SMTVisualizer:
    def __init__(self, result, manifest):
        self.result = result
        self.ii = result["ii"]
        self.schedule = result["schedule"]
        self.assignments = result.get("unit_assignments", {})
        self.manifest = manifest["hardware"]
        
    def render_multi_iter_timeline(self, num_iters=10):
        """Aggregate multiple iterations into one giant timeline."""
        # 1. Expand units
        units_list = []
        for u_meta in self.manifest["units"]:
            if u_meta.get("is_pulse"): continue
            for i in range(u_meta["count"]):
                units_list.append(f"{u_meta['name']}_{i}")
        for i in range(8): units_list.append(f"rtovr_{i}")
        
        # 2. Total simulation time
        # Last iter starts at (num_iters-1)*II, total length ~ (num_iters)*II + single_iter_len
        max_t = (num_iters - 1) * self.ii + max(self.schedule.values()) + 5
        grid = {u: [" . "] * (max_t + 1) for u in units_list}
        
        def get_char(op_type, iter_idx):
            # Optional: Use iter_idx to color or distinguish, 
            # for now, we'll use a number/char to show iteration 
            mapping = {"ur_read": "r", "ur_write": "w", "fpadd": "a", "fpmul": "m"}
            return mapping.get(op_type, "x")

        # 3. Superimpose Iterations
        for k in range(num_iters):
            offset = k * self.ii
            for inst_id, t_base in self.schedule.items():
                t = t_base + offset
                u_idx = self.assignments[inst_id]
                
                # Determine type
                op_type = "unknown"
                if inst_id.startswith("R_"): op_type = "ur_read"
                elif inst_id.startswith("W_"): op_type = "ur_write"
                elif inst_id.startswith("A"): op_type = "fpadd"
                elif inst_id.startswith("M"): op_type = "fpmul"
                
                char = get_char(op_type, k)
                target_unit = f"{op_type}_{u_idx}"
                
                # Mark Unit (using k % 10 to show which iteration is occupying it)
                if target_unit in grid:
                    grid[target_unit][t] = f" {k%10}{char}"
                    
                    # Mark Pulse
                    u_meta = next(um for um in self.manifest["units"] if um["name"] == op_type)
                    for p in u_meta.get("input_ports", []):
                        if t > 0: grid[f"rtovr_{p}"][t-1] = f" {k%10}o"
                    if u_meta.get("port_map"):
                        p = u_meta["port_map"][u_idx]
                        if t > 0: grid[f"rtovr_{p}"][t-1] = f" {k%10}o"

        # 4. Final Render (Condensed)
        lines = [f"Multi-Iter Horizontal Timeline (N={num_iters}, II={self.ii}, total_T={max_t})"]
        header = " Unit         | "
        for i in range(max_t + 1):
            header += f"{i % 10:01d} " if i % 10 == 0 else ". "
        lines.append(header)
        lines.append("-" * len(header))
        
        for u in units_list:
            row_str = f"{u:12} |" + "".join(grid[u])
            lines.append(row_str)
            
        return "\n".join(lines)
