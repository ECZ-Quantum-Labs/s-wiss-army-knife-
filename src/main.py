#!/usr/bin/env python3
import sys
import importlib.util
from pathlib import Path
import argparse
import json

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Find registry.py directly on disk (bypasses all import errors)
REGISTRY_PATH_1 = SCRIPT_DIR / "core" / "registry.py"
REGISTRY_PATH_2 = PROJECT_ROOT / "core" / "registry.py"

if REGISTRY_PATH_1.exists():
    REGISTRY_PATH = REGISTRY_PATH_1
    BLADES_DIR = SCRIPT_DIR / "blades"
elif REGISTRY_PATH_2.exists():
    REGISTRY_PATH = REGISTRY_PATH_2
    BLADES_DIR = PROJECT_ROOT / "blades"
else:
    print("[!] FATAL: registry.py not found in src/core/ or core/")
    sys.exit(1)

# Load registry module directly from file path
spec = importlib.util.spec_from_file_location("registry_module", REGISTRY_PATH)
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)
ModuleRegistry = registry_module.ModuleRegistry

def main():
    parser = argparse.ArgumentParser(prog="swiss-army")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-b", "--blade", required=True)
    parser.add_argument("-o", "--output", default="report.json")
    
    args = parser.parse_args()
    
    # Initialize registry and force correct blades path
    registry = ModuleRegistry()
    registry.blades_path = BLADES_DIR
    
    mod = registry.load_module(args.blade)
    
    if not mod:
        print(f"[!] Module '{args.blade}' not found in {BLADES_DIR}")
        sys.exit(1)
        
    class_name = "".join(w.capitalize() for w in args.blade.split("_"))
    if not hasattr(mod, class_name):
        print(f"[!] Class '{class_name}' not found in module.")
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

