# Using Nasaq with Codex

## Install from GitHub

Tell the agent:

```text
Install the Nasaq skill from:
https://github.com/y9090oussefwork/NASAQ_All_In_One

Inspect SKILL.md and README first. Install it in this project’s documented skill path,
do not overwrite a modified installation or change global host settings without approval.
Run a read-only validation and report the path, version and result.
```

Codex normally uses `.agents/skills/nasaq/`; other hosts may use their documented local skill path. If the host has no skill installer, the agent may clone or download the release and copy the `nasaq` folder after review.


Extract the release archive and place `nasaq/` at `<project>/.agents/skills/nasaq/`. Do not overwrite a modified installation. Open a fresh host session and select Nasaq or ask “Nasaq, inspect this project read-only.” Python 3.11+ and Git are needed for the coordination scripts. Source dependencies require separate approval and setup.

For a new project, ask for requirements and source recommendations first. Approve a bounded plan, then request execution to a named phase or through all approved phases. Ask “Nasaq, resume from saved state and inspect any interrupted actions” to continue. Preserve `.nasaq` state privately.

Spec Kit planning requires the official v1.1.2 checkout at `959e866caa3618bf3dc290d5dca33394365af9c6` and reviewed configuration described in the skill's web-integration reference. It is workflow-reference, not native integration. Nothing is downloaded just by installing the skill.

The host translates conversation into internal JSON events; users need not memorize source commands. If skill discovery fails, check its location and restart the session. Explicit file reading was tested; automatic discovery and full project resumption were not established by that smoke test.

See [official Codex skill documentation](https://developers.openai.com/codex/skills/) and [release limitations](RELEASE_STATUS.md). Accounts, service costs and sandbox policies belong to the host.

