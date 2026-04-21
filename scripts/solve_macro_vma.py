import sys
import os
import json
import argparse

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from smt_dsl_parser import SMTDSLParser
from pseudo_gen import generate_reports

def main():
    print("🚀 AOS 3.5 [II=1] Macro-Vector FMA Challenge")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--ii", type=int, default=1)
    arg_parser.add_argument("--dsl", type=str, default="flow/01_Ideation_Threads/TSK-010_DSL.json")
    arg_parser.add_argument("--output", type=str, default="flow/03_Output/TSK-010_Result.json")
    args = arg_parser.parse_args()

    manifest_path = "flow/02_Specs/Hardware_Manifest.json"
    dsl_path = args.dsl
    
    parser = SMTDSLParser(manifest_path)
    parser.load_instructions(dsl_path)
    
    # 💠 AOS 3.6: 理论 II 下限预判 (基于指令交叉存取)
    ii_min = 1
    for unit_meta in parser.scheduler.manifest["units"]:
        u_name = unit_meta["name"].upper()
        # 统计该单元上承担的指令流数量
        total_insts = len([i for i in parser.scheduler.instructions if i["unit"].upper() == u_name])
        # 理论下限 = 指令流数 / 单元实例数
        u_ii_min = (total_insts + unit_meta["count"] - 1) // unit_meta["count"]
        ii_min = max(ii_min, u_ii_min)
    
    print(f"📊 Resource Audit: Theoretical II_min = {ii_min}")
    
    # 从理论下限开始搜索
    result = parser.solve_modulo(initial_ii=ii_min, max_ii=ii_min + 32)
    
    if result:
        print(f"✅ SUCCESS! Macro-Compression Certified (II={result['ii']}).")
        
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Truth-Aligned Result stored: {args.output}")
    else:
        print("❌ FAILED: II=1 is not feasible with current constraints or DLY alignment.")

if __name__ == "__main__":
    main()
