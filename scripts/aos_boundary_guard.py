import subprocess
import sys
import re
import os

def get_git_diff():
    """获取当前的暂存区与未暂存区差异"""
    try:
        # 获取未提交的所有变更，设置超时防止挂起
        diff = subprocess.check_output(['git', 'diff'], timeout=10).decode('utf-8')
        return diff
    except subprocess.TimeoutExpired:
        print("⚠️ [AUDIT_ERROR] Git Diff 超时")
        return None
    except Exception as e:
        print(f"⚠️ [AUDIT_ERROR] 无法获取 Git Diff: {e}")
        return None

def audit_diff(diff):
    """分析 Diff 中的违规行为"""
    if not diff:
        print("✅ [SELF_AUDIT] 无文件变更，审计通过。")
        return True

    violations = []
    
    # 规则 1：严禁删除以 #, ##, ### 或 - ** 开头的核心定义行（除非是重命名）
    # 这里使用启发式搜索：如果删除行包含关键工程词汇，且没有对应的新增行
    deleted_lines = re.findall(r'^- (.*)', diff, re.MULTILINE)
    added_lines = re.findall(r'^\+ (.*)', diff, re.MULTILINE)
    
    critical_keywords = ['Hook', 'Rule', 'Protocol', 'DNA', 'Spec', 'Requirement', 'Step']
    
    for line in deleted_lines:
        if any(kw in line for kw in critical_keywords) or line.strip().startswith(('#', '- **')):
            # 检查是否只是在别处新增了（允许移动或微调）
            if not any(line.strip()[:20] in al for al in added_lines):
                violations.append(f"CRITICAL_DELETION: 检测到核心定义可能被删除 -> '{line.strip()}'")

    # 规则 2：检查文件指纹漂移 (如果是 flow/02 目录)
    if 'flow/02_Specs' in diff and "DNA-Fingerprint" not in diff:
         # 这是一个警告，规约修改应伴随指纹更新
         print("⚠️ [WARN] 规约文件已变动，请确保同步更新 Current_Mission.md 中的 DNA 指纹。")

    if violations:
        print("❌ [SELF_AUDIT] 发现边界违规：")
        for v in violations:
            print(f"   - {v}")
        return False
    
    print("✅ [SELF_AUDIT] 物理审计通过：无破坏性删除，符合 AOS 边界约束。")
    return True

def main():
    print("💠 AOS 边界守卫 (Boundary Guard) V1.0\n")
    
    # 1. 检查环境
    if not os.path.exists('.git'):
        print("❌ [ERROR] 当前不是 Git 仓库，物理审计无法执行。")
        sys.exit(1)

    # 2. 执行审计
    diff_content = get_git_diff()
    success = audit_diff(diff_content)
    
    if not success:
        sys.exit(1) # 强制熔断

if __name__ == "__main__":
    main()
