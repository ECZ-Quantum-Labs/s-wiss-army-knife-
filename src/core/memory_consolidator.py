
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Import vector utilities (graceful fallback if not installed)
try:
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))  # Add src to path
    from core.vector_utils import VectorKnowledgeBase
    VECTOR_ENABLED = True
except ImportError:
    VECTOR_ENABLED = False

class MemoryConsolidator:
    """
    24h Cyclic Memory Engine with Vector Intelligence (Public Stub)
    Reads reports, extracts patterns, stores in vector DB, creates knowledge snapshot.
    """
    
    def __init__(self, config_path: str = "src/config/ai_config.json", 
                 reports_dir: str = "reports", 
                 memory_dir: str = "memory"):
        # Load AI config
        self.config = self._load_config(config_path)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize vector DB if enabled
        self.vector_kb = None
        if VECTOR_ENABLED and self.config.get("vector_db", {}).get("enabled", False):
            try:
                self.vector_kb = VectorKnowledgeBase(self.config["vector_db"])
            except Exception as e:
                print(f"[!] Vector KB init skipped: {e}")
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        config_file = Path(path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}  # Fallback to empty config
    
    def run(self):
        print(f"[+] Starting 24h memory consolidation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_reports = list(self.reports_dir.glob("*.json"))
        if not all_reports:
            print("[!] No reports found. Skipping.")
            return

        consolidated = {
            "last_updated": datetime.now().isoformat(),
            "total_reports_processed": len(all_reports),
            "high_risk_patterns": [],
            "remediation_insights": [],
            "vector_storage": {
                "enabled": VECTOR_ENABLED and self.vector_kb is not None,
                "stored_count": 0,
                "similar_findings_found": 0
            },
            "system_notes": "Auto-consolidated by Swiss Army Knife Memory Engine v2"
        }

        for report_file in all_reports:
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for finding in data.get("results", []):
                    risk = finding.get("risk_level", "")
                    
                    # Store high-risk patterns
                    if risk in ["HIGH", "CRITICAL"]:
                        pattern = {
                            "endpoint": finding.get("endpoint", "unknown"),
                            "risk_score": finding.get("risk_score", 0),
                            "remediation": finding.get("remediation", "N/A")
                        }
                        consolidated["high_risk_patterns"].append(pattern)
                        
                        # Store in vector DB if enabled
                        if self.vector_kb:
                            if self.vector_kb.store_finding(finding):
                                consolidated["vector_storage"]["stored_count"] += 1
                            
                            # Search for similar past findings
                            query = f"{finding.get('endpoint')} {finding.get('remediation')}"
                            similar = self.vector_kb.search_similar(query, max_results=3)
                            if similar:
                                consolidated["vector_storage"]["similar_findings_found"] += len(similar)
                    
                    # Collect remediation insights
                    rem = finding.get("remediation")
                    if rem and rem != "N/A":
                        consolidated["remediation_insights"].append(rem)
                        
            except Exception as e:
                print(f"[!] Error reading {report_file.name}: {e}")

        # Deduplicate
        seen = {}
        for item in consolidated["high_risk_patterns"]:
            seen[item["endpoint"]] = item
        consolidated["high_risk_patterns"] = list(seen.values())
        consolidated["remediation_insights"] = list(set(consolidated["remediation_insights"]))

        # Save snapshot
        snapshot_name = f"knowledge_snapshot_{datetime.now().strftime('%Y%m%d')}.json"
        output_path = self.memory_dir / snapshot_name
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
            
        print(f"[+] Memory refreshed. Snapshot: {output_path}")
        if consolidated["vector_storage"]["enabled"]:
            print(f"[+] Vector DB: {consolidated['vector_storage']['stored_count']} stored, "
                  f"{consolidated['vector_storage']['similar_findings_found']} similar found")

if __name__ == "__main__":
    engine = MemoryConsolidator()
    engine.run()

