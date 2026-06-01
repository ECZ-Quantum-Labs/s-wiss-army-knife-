# 🗺️ Roadmap

> Development trajectory for Swiss Army Knife. All versions follow semantic versioning.

## 🔹 Phase 1: Core & Recon (v0.1 - v0.3) [In Progress]
- [x] Repository structure & licensing
- [ ] Recon Blade MVP: Subdomain enumeration, service fingerprinting, tech stack detection
- [ ] CLI foundation: `swiss-army recon -t <target> -o <format>`
- [ ] JSON/Markdown report generation
- [ ] GitHub Actions CI/CD pipeline

## 🔹 Phase 2: Vulnerability & Behavior (v0.4 - v0.6)
- [ ] Vuln Blade: Context-aware testing (XSS, SQLi, IDOR, RCE) with reduced false positives
- [ ] Behavior Blade: Response pattern analysis, anomaly detection, hidden endpoint discovery
- [ ] Smart rate-limiting & evasion handling
- [ ] Integration tests with mock targets

## 🔹 Phase 3: Fuzzing & Reporting (v0.7 - v0.9)
- [ ] Fuzzing Blade: Targeted input generation, grammar-aware payloads
- [ ] Report Blade: Automated HackerOne/Bugcrowd/CVE template generation
- [ ] CVSS v3.1 scoring integration
- [ ] Remediation suggestions engine

## 🔹 Phase 4: AI & Enterprise (v1.0+)
- [ ] AI Blade: Local LLM-assisted triage & payload suggestion
- [ ] Plugin system for custom blades
- [ ] Enterprise dashboard & team collaboration features
- [ ] Compliance exports (ISO 27001, NIST, OWASP)

## 📅 Release Cadence
- **MVP (v0.1)**: Recon only, stable CLI
- **Public Beta (v0.5)**: Recon + Vuln + Behavior
- **Stable Release (v1.0)**: Full suite + AI assistance

> *Roadmap is subject to change based on community feedback and security research priorities.*

