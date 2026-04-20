
import json
import sys

def visualize_schedule(manifest_path, result_path, max_cycles=40):
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)["hardware"]
    with open(result_path, 'r') as f:
        result = json.load(f)
    
    schedule = result["schedule"]
    ii = result["ii"]
    
    # 建立单元到字符的映射
    char_map = {
        "fpmul": "m",
        "fpadd": "a",
        "ur_read": "L",
        "ur_write": "S",
        "rtovr": "r"
    }
    
    print("\n💠 AOS 2.6 Physical Waveform Auditor")
    print(f"Task: {result['metadata'].get('spec_dna', 'UNKNOWN')} | II: {ii}")
    
    # Header
    header = "iq_name         |"
    for c in range(0, max_cycles + 1, 10):
        header += f"{c:<10}"
    print(header)
    print("-" * (len(header) + 10))
    
    # 模拟循环展开逻辑，展示流水线动态 (展示 10 次迭代)
    for unit in manifest["units"]:
        for u_idx in range(unit["count"]):
            row_label = f"{unit['name']}-{u_idx:<8}" if unit["count"] > 1 else f"{unit['name']:<16}"
            timeline = ["." for _ in range(max_cycles + 5)]
            
            # 找到映射到该单元的所有指令
            for inst_id, start_t in schedule.items():
                # 判断该指令是否属于此单元类型
                if inst_id.split("_")[1].lower() in unit["name"].lower():
                    # 模拟 10 次循环迭代
                    for iter_idx in range(10):
                        abs_t = start_t + (iter_idx * ii)
                        if abs_t < len(timeline):
                            char = char_map.get(unit["name"], "x")
                            timeline[abs_t] = char
            
            print(f"{row_label}| {' '.join(timeline)}")

if __name__ == "__main__":
    visualize_schedule(
        "flow/02_Specs/Hardware_Manifest.json", 
        "flow/04_Engineering_Log/MADD_Kernel_Certified_Result.json"
    )
