
from smt_modulo_core import SMTModuloScheduler
import json

def solve_madd_kernel():
    print("💠 AOS 2.6 [Task-002] Solving Modulo Kernel (II=1 Challenge)")
    
    # 1. 加载真理（硬件清单）
    scheduler = SMTModuloScheduler("flow/02_Specs/Hardware_Manifest.json")
    
    # 2. 定义内核成员
    # 只需要定义一个 MUL 和一个 ADD 的相对时序
    scheduler.add_instruction("K_MUL", "fpmul")
    scheduler.add_instruction("K_ADD", "fpadd")
    
    # 3. 建立因果依赖
    # ADD 必须在 MUL 结果产出后（Latency=4）启动
    dependencies = [("K_ADD", "K_MUL", 4)]
    
    # 4. 尝试寻找 II=1 的稳态解
    ii = 1
    result = scheduler.solve_modulo(ii, dependencies)
    
    if result["status"] == "CERTIFIED":
        print(f"✅ [SUCCESS] Kernel stabilized at II={ii}")
        
        # 🟢 AOS 2.6: Mandatory Content Audit Layer
        print("\n--- Physical Timing Audit [V2.6] ---")
        # 模拟审计逻辑：验证 ADD 是否真的在 MUL 产出后启动
        audit_pass = True
        for i in range(1): # 内核只有一个 MUL/ADD 对
            mul_t = result["schedule"]["K_MUL"]
            add_t = result["schedule"]["K_ADD"]
            if add_t < mul_t + 4:
                print(f"❌ [AUDIT_FAIL] Timing violation! ADD starting at {add_t} too early for MUL at {mul_t}")
                audit_pass = False
        
        if audit_pass:
            print("🛡️ [AUDIT_PASS] Cycle-accurate timing verified.")
            # 保存受控工件
            with open("flow/04_Engineering_Log/MADD_Kernel_Certified_Result.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"📑 [CEP] Certified Execution Plan saved with signature: {result['metadata']['truth_signature'][:12]}...")
        else:
            print("🛑 [BLOCK] Content rejected by Auditor. Solution will not be saved.")
    else:
        print(f"❌ [CRITICAL] solve_modulo failed: {result.get('error')}")

if __name__ == "__main__":
    solve_madd_kernel()
