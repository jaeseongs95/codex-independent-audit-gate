# Independent Audit Gate

[한국어](README.md) | English

`independent-audit-gate` is a Codex skill that checks whether a high-risk change has received an independent, evidence-based audit before it is marked complete.

Use it for changes whose failure could have a significant impact, including security, permissions, billing, data loss, schema migrations, production deployments, and global settings. An auditor who did not participate in the implementation examines the final change and validation evidence directly, then returns `PASS`, `FAIL`, or `BLOCKED`. After a real-world mutation, the auditor also checks the execution or deployment identifier, affected scope, partial failures, and whether recovery is needed.

## When to use it

Use this skill before executing or releasing changes involving:

- authentication, authorization, secrets, or external exposure;
- billing, refunds, pricing, or transaction execution;
- permanent deletion, bulk updates, personal data, or recovery procedures;
- schema migrations and compatibility changes;
- production deployments, public releases, infrastructure, or CI/CD; and
- settings that apply across an organization or project.

Do not use it for simple investigation, low-risk changes, ordinary code review, or design discussions without an implementation target. It also serves a different purpose from `independent-deliberation-panel`, which examines complex decisions from multiple perspectives and develops a consensus proposal. This skill does not create a panel or Judge; it checks that the final change has passed an independent audit and completion gate.

## Installation

### User scope

Windows PowerShell:

```powershell
git clone https://github.com/jaeseongs95/codex-independent-audit-gate "$env:USERPROFILE\.agents\skills\independent-audit-gate"
```

macOS or Linux:

```bash
git clone https://github.com/jaeseongs95/codex-independent-audit-gate "$HOME/.agents/skills/independent-audit-gate"
```

### Repository scope

To use the skill only in a specific project, run the following commands from that project's root.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path '.agents\skills' | Out-Null
git clone https://github.com/jaeseongs95/codex-independent-audit-gate '.agents\skills\independent-audit-gate'
```

macOS or Linux:

```bash
mkdir -p .agents/skills
git clone https://github.com/jaeseongs95/codex-independent-audit-gate .agents/skills/independent-audit-gate
```

Restart Codex if it does not discover the new skill automatically.

To pin a specific version, add `--branch v1.0.0 --depth 1` to the clone command.

## Usage

To invoke the skill directly, include `$independent-audit-gate` in your request.

```text
Use $independent-audit-gate to independently audit the final diff and test results for this permission change, then determine whether it can be marked complete.
```

```text
Use $independent-audit-gate to check rollback validation and the post-deployment state of this migration.
```

Automatic invocation is enabled. Codex may select this skill when a request involves executing, deploying, or completing a high-risk change.

## Verdicts

- `PASS`: Independence, final-target alignment, required evidence, finding remediation, and any required re-audit have all been verified.
- `FAIL`: At least one confirmed `blocking` finding remains open.
- `BLOCKED`: The audit cannot be completed because the auditor, final target, or required evidence is unavailable.

Passing tests alone is not enough for `PASS`. If the behavior or validation evidence changes after the audit, the previous verdict becomes stale and the affected scope must be audited again.

## Updating and removing

To update a user-scoped installation, run the following command.

Windows PowerShell:

```powershell
git -C "$env:USERPROFILE\.agents\skills\independent-audit-gate" pull --ff-only
```

macOS or Linux:

```bash
git -C "$HOME/.agents/skills/independent-audit-gate" pull --ff-only
```

To remove it, delete only the installed `independent-audit-gate` directory. Do not delete other skill directories or the parent `.agents` directory.

## Standalone and suite usage

You can install and use this skill on its own from this repository. To run it as part of a coordinated governance workflow, use the version included in [Agent Governance Suite](https://github.com/jaeseongs95/agent-governance-suite).

## Plugin integration

To include this skill in an orchestration plugin, copy this repository's `SKILL.md`, `agents/`, `references/`, and `scripts/` into `skills/independent-audit-gate/`. The plugin root must contain a `plugin.json` or `.codex-plugin/plugin.json` supported by the target tool. Manage `README.md`, `LICENSE`, `.github/`, `.gitattributes`, and `.gitignore` at the plugin root.

Follow the responsibility boundaries and handoff format in the [orchestrator integration guide](references/orchestrator-integration.md). The orchestrator classifies requests and assigns the auditor, while this skill performs the independent audit and returns `PASS`, `FAIL`, or `BLOCKED`. Run the following command from the copied skill directory to validate the component:

```bash
python scripts/validate_skill.py --strict
```

The validator detects supported plugin layouts automatically. Use `--profile plugin-component` to bypass automatic detection, or `--profile standalone` to validate this repository directly.

This skill uses `independent-deliberation-panel` only for development review and does not depend on it at runtime.

## Development validation

Windows:

```powershell
py -3 scripts/validate_skill.py --strict
py -3 scripts/test_plugin_component.py
```

macOS or Linux:

```bash
python3 scripts/validate_skill.py --strict
python3 scripts/test_plugin_component.py
```

The validator checks the package structure, metadata, local links, and artifacts that must not be included in the public repository. It does not prove the factual accuracy of an audit or the actual independence of an agent.

## License

[MIT License](LICENSE)
