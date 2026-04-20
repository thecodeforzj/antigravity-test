import re
import os
import sys

def check_markdown_integrity(file_path):
    try:
        # 尝试以 utf-8 读取，若失败则回退至 latin-1 (处理 BOM 或其他编码)
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return [f"Encoding Error: {str(e)}"]

    errors = []
    # 1. 检查 Frontmatter 完整性 (针对 Mission/Spec)
    # 我们只对 flow 目录下的 spec 进行强校验
    if 'flow/00' in file_path or 'flow/02' in file_path:
        if not content.strip().startswith('---'):
            errors.append("Missing YAML Frontmatter opening '---'")
        elif content.count('---') < 2:
            errors.append("Invalid YAML Header: Missing closing '---'")

    # 2. 检查必需的层级结构 (H1/H2)
    if not re.search(r'^#\s+', content, re.MULTILINE):
        errors.append("Missing H1 Title")

    # 3. 检查代码块闭合
    if content.count('```') % 2 != 0:
        errors.append("Unclosed code block (```)")

    return errors

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"🔦 [DOC_GUARD] Auditing: {target}")
    
    all_errors = []
    
    # 扫描所有 .md 文件，排除 .git 等目录
    files = []
    if os.path.isfile(target):
        files = [target]
    else:
        for root, dirs, fs in os.walk(target):
            if '.git' in dirs: dirs.remove('.git')
            for f in fs:
                if f.endswith('.md'): files.append(os.path.join(root, f))

    for f in files:
        errs = check_markdown_integrity(f)
        if errs:
            print(f"❌ {f}:")
            for e in errs: print(f"   - {e}")
            all_errors.extend(errs)
    
    if not all_errors:
        print("\n✅ All Documents are structurally sound.")
        sys.exit(0)
    else:
        print(f"\nTotal Errors: {len(all_errors)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
