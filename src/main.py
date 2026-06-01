
#!/usr/bin/env python3
"""
Swiss Army Knife - Modular Security Platform
Entry point with dynamic module registry integration.
Version: v0.2-alpha
"""
import argparse
import sys
import json
from pathlib import Path
from core.registry import ModuleRegistry

def main():
    parser = argparse.ArgumentParser(
        prog="swiss-army",
        description="Modular Security Platform for Hunters & Enterprises",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: swiss-army scan -t example.com -b sensitive_file_hunter -o report.json"
    )
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP")
    parser.add_argument("-b", "--blade", required=True, help="Blade module name")
    parser.add_argument("-o", "--output", default="report.json", help="Output file path")
    
    args = parser.parse_args()
    
    registry = ModuleRegistry()
    mod = registry.load_module(args.blade)
    
    if not mod:
        print(f"[!] Error: Module '{args.blade}' not found or failed to load.")
        sys.exit(1)
        
    # Dynamic instantiation using standard naming convention
    class_name = "".join(word.capitalize() for word in args.blade.split("_"))
    if not hasattr(mod, class_name):
        print(f"[!] Error: Class '{class_name}' not found in module '{args.blade}'.")
        sys.exit(1)
        
    blade_instance = getattr(mod, class_name)(target=args.target)
    blade_instance.run()
    output_data = blade_instance.export_findings()
    
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"[+] Scan completed. {output_data.get('findings_count', 0)} findings saved to {args.output}")
    sys.exit(0)

if __name__ == "__main__":
    main()

