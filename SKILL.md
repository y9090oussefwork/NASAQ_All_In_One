---
name: nasaq
description: >-
  Install and use the Nasaq Arabic-first web engineering coordination skill.
  Use when the user asks to install Nasaq from the Nasaq GitHub repository or to
  start, inspect, plan, design, implement, test, review, or resume a web project
  with Nasaq.
---

# Nasaq installer entrypoint

This repository is the public source for the Nasaq skill. When a host installs this repository as a skill, use the maintained skill directory at `skills/nasaq/` as the implementation source.

1. Inspect `skills/nasaq/SKILL.md`, `skills/nasaq/README.md`, and the root `README.md`.
2. Install the complete `skills/nasaq/` directory into the host's project-scoped skill path. For Codex use `.agents/skills/nasaq/`; preserve existing modified files and request approval before replacing them.
3. After installation, validate that `.agents/skills/nasaq/SKILL.md` exists and report the installed path, revision, and validation result.
4. Do not install Spec Kit, Django, PostgreSQL, Node, or any other external source merely because Nasaq was installed. Those are selected and approved later by Nasaq.
5. Do not change global host settings, publish code, or run project commands during installation unless the user explicitly asks.

After installation, the user can simply say `نسق، ابدأ` or `Nasaq, start` in the project. Load the installed `skills/nasaq/SKILL.md` as the authoritative runtime instructions. Read its linked references only when the requested workflow needs them.

The one-line installation request is:

> ثبّت مهارة نَسَق https://github.com/y9090oussefwork/NASAQ_All_In_One

This root file is an installer entrypoint; the full skill remains under `skills/nasaq/` so the repository can also contain public documentation, tests, and release material.


