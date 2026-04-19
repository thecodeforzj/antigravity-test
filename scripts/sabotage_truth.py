import json

def break_the_truth(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 🟢 INJECT MALICIOUS FAULT:
    # We shift 'A1' issue time from its proper place to 1 cycle later.
    # This WILL break the AC-PHYS-01 (Pulse == Ready) rule.
    data["schedule"]["A1"] += 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f"[FAULT-INJECT] Sabotaged A1 timing in {output_file}")

if __name__ == "__main__":
    break_the_truth("flow/03_Output/Taylor3_Result.json", "flow/03_Output/Taylor3_SABOTAGED.json")
