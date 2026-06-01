import requests
from typing import Dict, Any, List
import time

class EndpointFuzzer:
    """
    Offensive blade: Fuzzes common sensitive endpoints.
    Smart mode: Risk scoring + remediation suggestions.
    Public stub: Core intelligence resides in private module.
    """

    # Endpoint sensitivity weights (public-safe minimal list)
    ENDPOINT_WEIGHTS = {
        "/.env": 95,
        "/config.php": 90,
        "/backup.sql": 95,
        "/wp-config.php": 90,
        "/admin": 75,
        "/wp-admin": 70,
        "/phpmyadmin": 85,
        "/debug": 60,
        "/login": 40,
    }

    # Remediation templates (public-safe)
    REMEDIATION_TEMPLATES = {
        "/.env": "Restrict access via web server config; move sensitive data to environment variables with proper permissions",
        "/config.php": "Move configuration outside web root; add access controls; encrypt sensitive values",
        "/backup.sql": "Remove database dumps from web-accessible directories; implement proper backup rotation",
        "/admin": "Enforce strong authentication; implement rate limiting; add IP whitelisting",
        "/wp-admin": "Update WordPress core/plugins; use security plugins; disable file editing",
        "/phpmyadmin": "Restrict access by IP; use strong credentials; keep updated",
        "/debug": "Disable debug endpoints in production; use feature flags for staging",
        "/login": "Implement account lockout; add CAPTCHA; use HTTPS only",
        "default": "Review endpoint necessity; apply least-privilege access; monitor for abuse"
    }

    def __init__(self, target: str, config: Dict[str, Any] = None):
        self.target = target
        self.config = config or {}
        self.findings: List[Dict[str, Any]] = []
        self.timeout = self.config.get("timeout", 5)
        self.delay = self.config.get("delay", 0.5)
        self.debug_mode = self.config.get("debug", False)

    def _calculate_risk_score(self, endpoint: str, status: int, size: int) -> int:
        """Calculate risk percentage (0-100) based on heuristic rules."""
        base_weight = self.ENDPOINT_WEIGHTS.get(endpoint, 30)
        
        if status == 200:
            status_factor = 1.0
        elif status == 403:
            status_factor = 0.4
        elif status == 401:
            status_factor = 0.3
        else:
            status_factor = 0.1
        
        if 100 < size < 5000:
            size_factor = 1.0
        elif size < 100:
            size_factor = 0.5
        else:
            size_factor = 0.8
        
        score = int(min(100, base_weight * status_factor * size_factor))
        return score

    def _get_remediation(self, endpoint: str) -> str:
        return self.REMEDIATION_TEMPLATES.get(endpoint, self.REMEDIATION_TEMPLATES["default"])

    def _analyze_response(self, url: str, endpoint: str, response: requests.Response) -> Dict[str, Any]:
        status = response.status_code
        size = len(response.content)
        
        if status == 404 and not self.debug_mode:
            return None
        
        risk_score = self._calculate_risk_score(endpoint, status, size)
        
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "INFO"
        
        return {
            "url": url,
            "endpoint": endpoint,
            "status_code": status,
            "response_size": size,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "remediation": self._get_remediation(endpoint),
            "note": f"Status {status}, Size {size}B"
        }

    def run(self):
        base_url = f"https://{self.target}"
        
        for endpoint in self.ENDPOINT_WEIGHTS.keys():
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=self.timeout, allow_redirects=False)
                result = self._analyze_response(url, endpoint, response)
                if result:
                    self.findings.append(result)
                time.sleep(self.delay)
            except requests.exceptions.RequestException as e:
                if self.debug_mode:
                    self.findings.append({
                        "url": f"{base_url}{endpoint}",
                        "endpoint": endpoint,
                        "status": "ERROR",
                        "error": str(e),
                        "risk_score": 0,
                        "risk_level": "INFO",
                        "remediation": "Check network connectivity and target availability",
                        "note": "Request failed"
                    })

    def export_findings(self) -> Dict[str, Any]:
        critical = [f for f in self.findings if f.get("risk_level") == "CRITICAL"]
        high = [f for f in self.findings if f.get("risk_level") == "HIGH"]
        
        return {
            "blade": "endpoint_fuzzer",
            "target": self.target,
            "findings_count": len(self.findings),
            "critical_count": len(critical),
            "high_risk_count": len(high),
            "results": sorted(self.findings, key=lambda x: x.get("risk_score", 0), reverse=True)
        }

