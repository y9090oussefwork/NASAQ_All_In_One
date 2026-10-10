# Nasaq

[العربية](README.md) · [Usage](docs/USAGE_EN.md) · [Status](docs/RELEASE_STATUS.md) · [MIT](LICENSE)

Arabic-first, English-selectable coordination for web development inside a coding host. Nasaq collects requirements, records approvals and progress, and reuses specialist projects behind one conversational interface.

This is a public experimental release, not an autonomous application factory. Codex is the initial host. Source is free under MIT; model accounts and external services have separate terms and costs.

Download `skill.zip` from Releases, extract it, and place the complete `nasaq` folder at `<project>/.agents/skills/nasaq`. Preserve existing modifications. Open a fresh Codex session, select the skill if available, and ask: “Nasaq, start a web project. Collect requirements and propose sources before any download or execution.”

Implemented: bilingual intake, approvals, state and recovery controls, project-scoped installation lifecycle, pinned Spec Kit workflow-reference planning, limited Django/Bandit execution, and source instruction handoffs. Dependencies are opt-in and not bundled.

Limitations: the Codex smoke test explicitly requested the skill file and resumed that conversation; automatic discovery and full project continuation remain unproven. Human acceptance and measured direct-versus-Nasaq comparison are pending. Claude/Cursor are deferred. Web only.

Run `python -m unittest discover -s skills/nasaq/tests -q` with Python 3.11+ and Git. Build with `python scripts/build_release.py`. See CONTRIBUTING.md and THIRD_PARTY_NOTICES.md. Historical documents and archives describe earlier milestones, not current certification.
