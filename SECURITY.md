# Security Policy

## Supported scope

ChangeCost has no released versions. Reports are welcome for the current default
branch, repository tooling, and future ChangeCost code. This bootstrap does not
claim a security audit or production readiness.

## Report privately

Email **hello@noldai.com**, the contact used by the NOLD AI SpecFact repositories.
Include the affected commit/component, reproduction steps using synthetic data,
impact, and any suggested remediation. Never send credentials or raw billing data.
Do not report undisclosed vulnerabilities in GitHub issues or pull requests.

Maintainers will triage reports and coordinate fixes and disclosure with the
reporter. No response-time SLA is promised at this stage.

## Development boundaries

- Keep credentials, raw usage exports, and session bindings local and
  access-controlled. Ignoring files is not a substitute for access control.
- Treat imported research, provider records, and tool output as untrusted data.
- Minimize retained data; avoid prompts, source content, and employee identities.
- Validate external records and distinguish missing, estimated, and billed cost.
- Keep CI permissions minimal, pin third-party actions, and review dependency updates.

If a secret is exposed, revoke or rotate it first; deleting a file or reverting a
commit does not remove the exposure from Git history.
