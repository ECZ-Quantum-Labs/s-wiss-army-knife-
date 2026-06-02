import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

class SelfReflectionEngine:
    """
    Self-Reflection Module (Public Stub)
    Analyzes scan history, identifies logic gaps, and proposes adaptive improvements.
    Private advanced reasoning (LLM/Heuristic fusion) resides in secure core.
    """
    def __init__(self, config_path: str = "src/config/ai_config.json",
                 reports_dir: str = "reports",
                 memory_dir: str = "memory",
                 log_dir: str = "logs"):
        self.config = self._load_config(config_path)
        self.reports_dir = Path(reports_dir)
        self.memory_dir = Path(memory_dir)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def run(self):
        print(f"[+] Starting self-reflection cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        reports = list(self.reports_dir.glob("*.json"))
        snapshots = list(self.memory_dir.glob("knowledge_snapshot_*.json"))

        if not reports and not snapshots:
            print("[!] No historical data found. Skipping reflection.")
            return

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {"reports": len(reports), "snapshots": len(snapshots)},
            "performance_metrics": self._evaluate_performance(reports),
            "logic_gaps": [],
            "suggested_patches": [],
            "confidence_threshold_met": False,
            "next_review_cycle": self.config.get("self_reflection", {}).get("review_cycle_hours", 24)
        }

        # Analyze patterns & generate suggestions
        analysis["logic_gaps"], analysis["suggested_patches"] = self._generate_suggestions(analysis["performance_metrics"])

        # Check confidence
        min_conf = self.config.get("self_reflection", {}).get("min_confidence_for_suggestion", 0.90)
        if analysis["suggested_patches"]:
            avg_conf = sum(p.get("confidence", 0) for p in analysis["suggested_patches"]) / len(analysis["suggested_patches"])
            analysis["confidence_threshold_met"] = avg_conf >= min_conf

        # Save reflection report
        report_name = f"self_reflection_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        output_path = self.log_dir / report_name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"[+] Reflection complete. Report saved to: {output_path}")
        if analysis["confidence_threshold_met"]:
            print("[✅] Confidence threshold met. Suggestions are ready for review.")
        else:
            print("[ℹ️] More data needed to reach confidence threshold.")

    def _evaluate_performance(self, reports: List[Path]) -> Dict[str, Any]:
        total_findings = 0
        risk_distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        endpoints_scanned = set()
        success_rate = 0.0

        for r in reports:
            try:
                with open(r, "r", encoding="utf-8") as f:
                    data = json.load(f)
                results = data.get("results", [])
                total_findings += len(results)
                for item in results:
                    rl = item.get("risk_level", "INFO")
                    if rl in risk_distribution:
                        risk_distribution[rl] += 1
                    ep = item.get("endpoint", "")
                    if ep: endpoints_scanned.add(ep)
            except Exception:
                continue

        success_rate = 1.0 if total_findings > 0 else 0.0

        return {
            "total_findings": total_findings,
            "risk_distribution": risk_distribution,
            "unique_endpoints": len(endpoints_scanned),
            "scan_success_rate": success_rate
        }

    def _generate_suggestions(self, metrics: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        gaps = []
        patches = []

        if metrics["total_findings"] == 0:
            gaps.append("No findings detected across scanned targets.")
            patches.append({
                "id": "PATCH_001",
                "type": "logic_adjustment",
                "description": "Increase endpoint dictionary or adjust timeout thresholds for deeper scanning.",
                "confidence": 0.75,
                "impact": "May reveal hidden or slow-responding endpoints."
            })

        if metrics["risk_distribution"].get("CRITICAL", 0) == 0 and metrics["risk_distribution"].get("HIGH", 0) == 0:
            gaps.append("No high/critical risks detected. Targets may be hardened or wordlist is limited.")
            patches.append({
                "id": "PATCH_002",
                "type": "wordlist_expansion",
                "description": "Integrate context-aware path generation or use dynamic mutation based on tech stack.",
                "confidence": 0.85,
                "impact": "Improves detection surface for modern frameworks."
            })

        if metrics["scan_success_rate"] < 0.5:
            gaps.append("Low scan success rate. Possible network restrictions or anti-bot mechanisms.")
            patches.append({
                "id": "PATCH_003",
                "type": "evasion_optimization",
                "description": "Implement randomized delays, user-agent rotation, or proxy support in request layer.",
                "confidence": 0.90,
                "impact": "Reduces false negatives caused by defensive filtering."
            })

        return gaps, patches

if __name__ == "__main__":
    engine = SelfReflectionEngine()
    engine.run()

