import json
import sys
import os

def visualize_schedule(manifest_path, result_path, max_cycles=120):
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)["hardware"]
    with open(result_path, 'r') as f:
        result = json.load(f)
    
    schedule = result["schedule"]
    unit_assignments = result.get("unit_assignments", {})
    ii = result["ii"]
    
    def get_tag(inst_id, iter_idx):
        first = inst_id[0].lower() # a, m, r, L, S
        if first == 'u': # ur_read -> L
            first = 'L' if 'read' in inst_id else 'S'
        return f"{iter_idx}{first}"

    print("\n💠 AOS 4.0 High-Resolution Waveform Auditor [ITERATION TAGGING]")
    print(f"File: {os.path.basename(result_path)} | II: {ii}")
    
    # 精确对齐的 Header (每 3 格为一个时隙，因为 " 0a" 是两个字符加一个空格)
    # 不，我们改用更清晰的 3-char 槽位
    header = "iq_name         |"
    for c in range(max_cycles):
        if c % 10 == 0:
            header += f"{c:<30}"
    print(header)
    
    sub_header = "                |"
    for c in range(max_cycles):
        sub_header += f"{c%10:<3}"
    print(sub_header)
    print("-" * (max_cycles * 3 + 20))
    
    for unit in manifest["units"]:
        u_name = unit["name"]
        for u_idx in range(unit["count"]):
            row_label = f"{u_name}-{u_idx:<8}"
            timeline = [" . " for _ in range(max_cycles)]
            
            for inst_id, start_t in schedule.items():
                # 指令类型匹配
                is_match = False
                if 'mul' in u_name and inst_id[0] == 'M': is_match = True
                elif 'add' in u_name and inst_id[0] == 'A': is_match = True
                elif 'read' in u_name and inst_id[0] == 'L': is_match = True
                elif 'rtovr' in u_name and inst_id[0] == 'R': is_match = True
                elif 'write' in u_name and inst_id[0] == 'S': is_match = True
                
                if is_match:
                    if unit_assignments.get(inst_id, 0) == u_idx:
                        # 模拟展开 20 次迭代
                        for iter_idx in range(20):
                            abs_t = start_t + iter_idx * ii
                            if abs_t < max_cycles:
                                timeline[abs_t] = f"{iter_idx:1}{inst_id[0].lower():1} "
            
            # 过滤掉全空行
            if "".join(timeline).count('.') < max_cycles:
                print(f"{row_label}|{''.join(timeline)}")

if __name__ == "__main__":
    m_path = "flow/02_Specs/Hardware_Manifest.json"
    r_path = sys.argv[1] if len(sys.argv) > 1 else "flow/03_Output/Taylor4_DSL_Result.json"
    visualize_schedule(m_path, r_path)
