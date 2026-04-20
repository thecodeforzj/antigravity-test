import json
import os
import sys
from datetime import datetime

STATUS_FILE = 'flow/00_Mission_Control/AOS_Status.json'

PIPELINE_ORDER = [
    'IDLE', 'SYNCED', 'HYDRATED', 'PROPOSED', 
    'DEVELOPING', 'AUDITED', 'CLOSED'
]

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {"current_state": "IDLE", "history": []}
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def save_status(status):
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def transit(target_state, task_id=None):
    status = load_status()
    current = status['current_state']
    
    if target_state not in PIPELINE_ORDER:
        print(f"❌ Error: Unknown state '{target_state}'")
        sys.exit(1)
        
    current_idx = PIPELINE_ORDER.index(current)
    target_idx = PIPELINE_ORDER.index(target_state)
    
    # 允许回到 IDLE，但严禁跳级增长 (跳过中间阶段)
    if target_state != 'IDLE' and target_idx != current_idx + 1:
        print(f"❌ [BLOCKED] Protocol Violation!")
        print(f"   Cannot transit from '{current}' directly to '{target_state}'.")
        print(f"   Mandatory next step is: '{PIPELINE_ORDER[current_idx + 1]}'")
        sys.exit(1)
        
    # 执行状态迁移
    status['current_state'] = target_state
    status['task_context'] = task_id
    status['history'].append({
        "timestamp": datetime.now().isoformat(),
        "from": current,
        "to": target_state,
        "task_id": task_id
    })
    save_status(status)
    print(f"✅ [TRANSIT] Pipeline state updated: {current} -> {target_state}")

def report():
    status = load_status()
    print(f"💠 Current AOS Pipe-State: \033[96m[{status['current_state']}]\033[0m")
    if status['task_context']:
        print(f"📍 Active Task: {status['task_context']}")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "REPORT"
    if action == "TRANSIT":
        transit(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif action == "REPORT":
        report()
    elif action == "RESET":
        transit('IDLE')
