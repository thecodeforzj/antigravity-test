
from smt_modulo_core import SMTModuloScheduler
import json

def run_madd_task():
    print("🚀 AOS 2.6 [Task-002] Initiating MADD Scheduling (a*b+c) x 10")
    
    # 1. 初始化调度器（加载物理真理）
    scheduler = SMTModuloScheduler("flow/02_Specs/Hardware_Manifest.json")
    
    # 2. 构建 10 组指令
    # 每组包含一个 fpmul 和一个 fpadd
    dependencies = []
    for i in range(10):
        mul_id = f"MUL_{i}"
        add_id = f"ADD_{i}"
        
        scheduler.add_instruction(mul_id, "fpmul")
        scheduler.add_instruction(add_id, "fpadd")
        
        # 建立因果链：ADD_i 依赖于 MUL_i
        # 格式: (child_id, parent_id, offset)
        dependencies.append((add_id, mul_id, 4))
        
    # 3. 寻找最小 Initiation Interval (II)
    # 我们从 II=1 开始尝试（理论极限由资源总量决定）
    # MUL 资源只有 1 个，ADD 资源只有 1 个，所以 II 必须 >= 10
    for ii in range(1, 20):
        print(f"🔍 Testing [II={ii}]...")
        result = scheduler.solve_modulo(ii, dependencies)
        if result:
            print(f"✅ [SUCCESS] Found valid schedule at II={ii}")
            # 导出调度结果
            with open("flow/04_Engineering_Log/Task-002_RESULT.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"📑 Results crystallized to: flow/04_Engineering_Log/Task-002_RESULT.json")
            break
        else:
            print(f"❌ [FAIL] II={ii} is infeasible.")

if __name__ == "__main__":
    run_madd_task()
