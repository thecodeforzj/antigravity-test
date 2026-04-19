import os
import re

def get_project_info(path):
    mc_path = os.path.join(path, "flow", "00_Mission_Control", "Current_Mission.md")
    if not os.path.exists(mc_path):
        return "Unknown"
    with open(mc_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'project_name:\s*"(.*)"', content)
        return match.group(1) if match else "Unknown"

def count_md_files(path):
    if not os.path.exists(path):
        return "N/A"
    files = [f for f in os.listdir(path) if f.endswith(".md") and f.lower() != "readme.md"]
    return len(files)

def generate_dashboard(root_path):
    project = get_project_info(root_path)
    stages = [
        ("P0: Mission", "flow/00_Mission_Control"),
        ("P1: Ideate", "flow/01_Ideation_Threads"),
        ("P2: Specs", "flow/02_Crystallized_Specs"),
        ("P3: Develop", "app"),
        ("P4: Retro", "flow/04_Engineering_Log")
    ]
    
    output = []
    output.append(f"### AOS Status Dashboard: {project}")
    output.append("| Stage | Path | Files | Status |")
    output.append("| :--- | :--- | :--- | :--- |")
    
    for name, rel_path in stages:
        full_path = os.path.join(root_path, rel_path)
        count = count_md_files(full_path)
        # Use ASCII-friendly status first to avoid encoding crashes
        status_icon = "[OK]" if count != "N/A" and (isinstance(count, int) and count > 0) else "[EMPTY]"
        output.append(f"| {name} | `{rel_path}` | {count} | {status_icon} |")
    
    print("\n".join(output).encode('utf-8', errors='replace').decode('utf-8'))

if __name__ == "__main__":
    import sys
    # Handle Windows UTF-8 output
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    generate_dashboard(".")
