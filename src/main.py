#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent  # This is src/
PROJECT_ROOT = SCRIPT_DIR.parent  # This is swiss-army-knife/

# Add both to sys.path (bulletproof method)
for path in [str(PROJECT_ROOT), str(SCRIPT_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Auto-create __init__.py files if missing
init_files = [
    SCRIPT_DIR / "core" / "__init__.py",
    SCRIPT_DIR / "blades" / "__init__.py"
]

for init_file in init_files:
    init_file.parent.mkdir(parents=True, exist_ok=True)
    if not init_file.exists():
        init_file.touch()
        print(f"[+] Created missing file: {init_file}")

# Now import
try:
    from core.registry import ModuleRegistry
except ImportError as e:
    print(f"[!] FATAL: Cannot import ModuleRegistry")
    print(f"[!] Error: {e}")
    print(f"[!] Debug info:")
    print(f"    PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"    SCRIPT_DIR: {SCRIPT_DIR}")
    print(f"    sys.path: {sys.path[:3]}")
    sys.exit(1)

import argparse
import json

def main():
    parser = argparse.ArgumentParser(
        prog="swiss-army",
        description="Modular Security Platform for Hunters & Enterprises"
    )
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-b", "--blade", required=True)
    parser.add_argument("-o", "--output", default="report.json")
    
    args = parser.parse_args()
    
    registry = ModuleRegistry()
    mod = registry.load_module(args.blade)
    
    if not mod:
        print(f"[!] Module '{args.blade}' not found")
        sys.exit(1)
        
    class_name = "".join(w.capitalize() for w in args.blade.split("_"))
    blade_class = getattr(mod, class_name)
    blade_instance = blade_class(target=args.target)
    blade_instance.run()
    output_data = blade_instance.export_findings()
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"[+] Done. {output_data.get('findings_count', 0)} findings → {args.output}")
    sys.exit(0)

if __name__ == "__main__":
    main()

