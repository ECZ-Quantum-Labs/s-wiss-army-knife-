import os
import json
import glob
from datetime import datetime
from pathlib import Path

class MemoryConsolidator:
    """
    24h Cyclic Memory Engine (Public Stub)
    Reads past reports, extracts patterns, and creates a fresh knowledge snapshot.
    Private AI/Vector logic plugs into this structure later.
    """
    
    def __init__(self, reports_dir="reports", memory_dir="memory"):
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

    def run(self):
        print(f"[+] Starting 24h memory consolidation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_reports = list(self.reports_dir.glob("*.json"))
        if not all_reports:
            print("[!] No reports found in directory. Skipping.")
            return

        consolidated = {
            "last_updated": datetime.now().isoformat(),
            "total_reports_processed": len(all_reports),
            "high_risk_patterns": [],
            "remediation_insights": [],
            "system_notes": "Auto-consolidated by Swiss Army Knife Memory Engine"
        }

        for report_file in all_reports:
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for finding in data.get("results", []):
                    risk = finding.get("risk_level", "")
                    if risk in ["HIGH", "CRITICAL"]:
                        consolidated["high_risk_patterns"].append({
                            "endpoint": finding.get("endpoint", "unknown"),
                            "risk_score": finding.get("risk_score", 0),
                            "remediation": finding.get("remediation", "N/A")
                        })
                    
                    rem = finding.get("remediation")
                    if rem and rem != "N/A":
                        consolidated["remediation_insights"].append(rem)
            except Exception as e:
                print(f"[!] Error reading {report_file.name}: {e}")

        # Remove duplicates
        seen_endpoints = {}
        for item in consolidated["high_risk_patterns"]:
            seen_endpoints[item["endpoint"]] = item
        consolidated["high_risk_patterns"] = list(seen_endpoints.values())
        consolidated["remediation_insights"] = list(set(consolidated["remediation_insights"]))

        # Save snapshot
        snapshot_name = f"knowledge_snapshot_{datetime.now().strftime('%Y%m%d')}.json"
        output_path = self.memory_dir / snapshot_name
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
            
        print(f"[+] Memory refreshed. Snapshot saved to: {output_path}")

if __name__ == "__main__":
    engine = MemoryConsolidator()
    engine.run()

