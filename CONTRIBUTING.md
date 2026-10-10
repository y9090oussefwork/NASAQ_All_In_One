# Contributing

Open an issue describing the requirement, existing source that might cover it, and expected evidence. Keep changes scoped to web. Prefer source reuse over duplicate implementations. Never commit credentials, project conversations, databases or downloaded toolchains.

Use Python 3.11+ and Git. Run `python -m unittest discover -s skills/nasaq/tests -q` before a pull request. Add meaningful regression tests for behavior changes. Record real execution separately from mocks and host-applied instructions. Document versions, licenses, side effects and permission boundaries for new adapters. Do not mark skipped or blocked checks passed.

Submit a pull request explaining behavior, validation and limitations. Contributions to original Nasaq code are under MIT; retain third-party notices.
