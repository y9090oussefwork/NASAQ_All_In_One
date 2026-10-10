# Curated tool catalog

Reviewed against primary documentation on **2026-10-09**. This is a curated shortlist, not an exhaustive inventory, a comparative benchmark, a security endorsement or a list of preinstalled components. Actual integrations were not exercised here. Reverify origin, current license, release status, host/OS support, permissions and install method before use.

Choose one primary workflow provider, one compatible design direction provider, and the smallest useful test/security toolset. Language-specific tools must match the actual language even when their platform tag matches. Optional reference standards do not require a runtime installation.

| Tool | Type | Purpose | Selection limit |
|---|---|---|---|
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | workflow | Structured per-change specifications | Keep existing or select as one spec provider; do not combine competing orchestration. |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | workflow | Structured specifications, planning and verification processes | An alternative provider for new or existing projects; choose deliberately. |
| [Superpowers](https://github.com/obra/superpowers) | skills | Planning, debugging, testing and review workflows | Select relevant compatible skills; inspect mandatory hooks and overlapping orchestration. |
| [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) | workflow | Product and engineering workflow coordination | Optional alternative when its process matches the project; not an additional default orchestrator. |
| [GSD Core](https://github.com/open-gsd/gsd-core) | workflow | Alternative context and delivery orchestration | Evaluate separately; old gsd-build/get-shit-done repository is archived and points here. |
| [Serena](https://github.com/oraios/serena) | semantic-navigation | Symbol-aware code retrieval and editing | Use only for supported languages/backends; review component licenses, permissions and data flow. |
| [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding) | mapping | Derived architecture and component maps | Requires appropriate analysis/model setup; review code disclosure and verify inferred maps. |
| [Repomix](https://github.com/yamadashy/repomix) | context | Selective repository export for model context | Use scoped exports; manually exclude secrets/customer data; not persistent semantic memory. |
| [Mermaid](https://github.com/mermaid-js/mermaid) | mapping | Text-based diagrams versioned with documentation | Use focused diagrams; layout does not prove the architecture matches runtime. |
| [Context7](https://github.com/upstash/context7) | documentation | Library documentation retrieval | Optional supplement to official docs; verify requested package/version and permissions. |
| [Impeccable](https://github.com/pbakaus/impeccable) | design | Frontend design guidance and critique | Preferred candidate for non-generic web UI; not native Android/Windows certification. |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | design | Style, palette and typography research | Use as design research; verify current free/paid boundaries, assets and native conventions. |
| [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | design | Distinctive intentional frontend design guidance | Lean alternative; avoid conflicting aesthetic providers. |
| [Playwright](https://playwright.dev/docs/test-snapshots) | testing | Browser E2E and visual comparison | Requires browser/runtime support and controlled screenshot environment. |
| [Maestro](https://github.com/mobile-dev-inc/Maestro) | testing | UI end-to-end flows | Check current OS/device support; no substitute for native performance benchmarks. |
| [FlaUI](https://github.com/FlaUI/FlaUI) | testing | Windows UI Automation testing | Requires suitable Windows target and automation support. |
| [Grafana k6](https://grafana.com/docs/k6/latest/) | performance | Service load and capacity testing | Only owned/authorized test targets; model traffic and resource stop limits. |
| [Schemathesis](https://schemathesis.readthedocs.io/en/stable/) | testing | Schema-driven API property tests | Requires supported schema and isolated data; add independent business/auth tests. |
| [Testcontainers](https://github.com/testcontainers) | testing | Integration test infrastructure libraries | Choose language-specific library; requires a supported container runtime. |
| [Knip](https://github.com/webpro-nl/knip) | code-quality | Unused JS/TS files, exports and dependency candidates | JS/TS only; investigate dynamic wiring/public consumers before deletion. |
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) | code-quality | JS/TS dependency rules and visualization | Use for compatible languages; adapt rules to real module boundaries. |
| [jscpd](https://github.com/kucherenko/jscpd) | code-quality | Copy/paste duplication detection | Investigate meaningful duplication; do not abstract all similar code automatically. |
| [Semgrep](https://github.com/semgrep/semgrep) | security | Static analysis with supported rules/languages | Verify language/rules coverage, licensing and local/cloud behavior. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | security | Secret detection | Detection is imperfect; restrict data exposure independently. |
| [OSV-Scanner](https://github.com/google/osv-scanner) | security | Dependency vulnerability scanning | Verify ecosystem/lockfile coverage; a clean scan is not proof of security. |
| [ZAP](https://github.com/zaproxy/zaproxy) | security | Authorized dynamic web/API security testing | Use an isolated approved target and bounded scan; never scan competitors. |
| [Trail of Bits skills](https://github.com/trailofbits/skills) | skills | Contextual security and differential review workflows | Optional security specialist aid; observe upstream license and host support. |
| [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) | performance | Android startup and runtime scenario measurement | Use release-like builds and representative physical hardware for real-device claims. |
| [Android Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/measure-baselineprofile) | performance | Profile-guided startup/runtime optimization | Measure benefit; do not promise a universal percentage gain. |
| [Windows/.NET profiling tools](https://learn.microsoft.com/en-us/windows/apps/develop/performance/profiling-tools) | performance | CPU, memory, I/O and UI responsiveness investigation | Choose native profiler for the target runtime and OS. |
| [Core Web Vitals](https://web.dev/articles/vitals) | performance-reference | User-centric web performance measures | Distinguish field percentiles from lab diagnostics. |
| [OpenTelemetry](https://opentelemetry.io/docs/) | observability | Instrumentation and export of observability signals | Select supported SDKs and a backend; bound telemetry overhead and sensitive data. |
| [OWASP ASVS](https://owasp.org/projects/asvs) | security-reference | Web/application security verification requirements | Select relevant controls and record the standard version; not certification. |
| [OWASP MASVS/MASTG](https://mas.owasp.org/) | security-reference | Mobile security requirements and testing guidance | Select applicable mobile controls; pair requirements with evidence. |

## Important fresh checks
The old https://github.com/gsd-build/get-shit-done repository was archived and directs users to GSD Core. Do not infer current status from an old recommendation. Serena uses component-specific licensing; never assume all items here are MIT licensed. Commercial/cloud features may have additional terms even when a repository is open.

The machine-readable equivalent is `assets/tool-registry.json`. No upstream source or license text is copied into this bundle.
