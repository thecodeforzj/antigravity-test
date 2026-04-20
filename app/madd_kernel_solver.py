
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
    
    if result:
        print(f"✅ [SUCCESS] Kernel stabilized at II={ii}")
        # 保存内核调度指纹
        with open("flow/04_Engineering_Log/MADD_Kernel_Result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("📑 Kernel Schedule crystallized.")
    else:
        print("❌ [CRITICAL] II=1 is physically blocked. This should not happen for single unit.")

if __name__ == "__main__":
    solve_madd_kernel()
