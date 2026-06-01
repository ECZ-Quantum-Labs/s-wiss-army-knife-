#!/usr/bin/env python3
import sys
import importlib.util
from pathlib import Path
import argparse
import json

# Get absolute paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Direct path to registry.py
REGISTRY_FILE = SCRIPT_DIR / "core" / "registry.py"

if not REGISTRY_FILE.exists():
    print(f"[!] FATAL: {REGISTRY_FILE} does not exist!")
    print(f"[!] SCRIPT_DIR: {SCRIPT_DIR}")
    print(f"[!] Files in src/core/: {list((SCRIPT_DIR / 'core').glob('*')) if (SCRIPT_DIR / 'core').exists() else 'N/A'}")
    sys.exit(1)

# Load registry directly from file
spec = importlib.util.spec_from_file_location("registry", REGISTRY_FILE)
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)
ModuleRegistry = registry_module.ModuleRegistry

# Set blades directory
BLADES_DIR = SCRIPT_DIR / "blades"

def main():
    parser = argparse.ArgumentParser(prog="swiss-army")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-b", "--blade", required=True)
    parser.add_argument("-o", "--output", default="report.json")
    
    args = parser.parse_args()
    
    # Initialize registry with correct blades path
    registry = ModuleRegistry()
    registry.blades_path = BLADES_DIR
    
    mod = registry.load_module(args.blade)
    
    if not mod:
        print(f"[!] Module '{args.blade}' not found in {BLADES_DIR}")
        sys.exit(1)
        
    class_name = "".join(w.capitalize() for w in args.blade.split("_"))
    if not hasattr(mod, class_name):
        print(f"[!] Class '{class_name}' not found in module")
        sys.exit(1)
        
    blade_class = getattr(mod, class_name)
    blade_instance = blade_class(target=args.target)
    blade_instance.run()
    output_data = blade_instance.export_findings()
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"[+] Done. {output_data.get('findings_count', 0)} findings -> {args.output}")
    sys.exit(0)

if __name__ == "__main__":
    main()


