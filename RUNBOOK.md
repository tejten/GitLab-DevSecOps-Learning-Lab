# GitLab DevSecOps Learning Runbook

This runbook captures the commands used to set up and continue the GitLab
DevSecOps learning lab.

## Project Details

- Local folder: `/Users/ttenmattam/Documents/Learn Gitlab`
- GitLab remote: `git@gitlab.com:collibra-group/Collibra-project.git`
- Default branch: `main`

## 1. Go To The Project

```bash
cd "/Users/ttenmattam/Documents/Learn Gitlab"
git status --short --branch
git remote -v
```

## 2. Configure Git Identity

Use your own name and email if setting this up again in another project.

```bash
git config --local user.name "Your Name"
git config --local user.email "your.email@example.com"

git config --get user.name
git config --get user.email
```

## 3. Configure The GitLab Remote

If the repository has no remote yet:

```bash
git remote add origin git@gitlab.com:collibra-group/Collibra-project.git
```

If the remote already exists but is wrong:

```bash
git remote set-url origin git@gitlab.com:collibra-group/Collibra-project.git
```

Check it:

```bash
git remote -v
```

## 4. Use `main` As The Default Branch

```bash
git branch -m main
git status --short --branch
```

## 5. Set Up SSH Access To GitLab

Show your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the output into GitLab:

1. Open `https://gitlab.com/-/user_settings/ssh_keys`.
2. Paste the public key.
3. Use a clear title, such as your computer name.
4. Choose `Authentication & Signing` if GitLab asks for a usage type.
5. Save the key.

Test SSH:

```bash
ssh -T git@gitlab.com
```

If your key has a passphrase on macOS, add it to the agent/keychain:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
ssh-add -l
```

Common failure:

```text
git@gitlab.com: Permission denied (publickey).
```

That means GitLab does not recognize the SSH key being offered by your machine,
or the key is not loaded. Add the public key in GitLab and retry.

## 6. Lab 1: First GitLab Pipeline

Stage and commit the first README and CI file:

```bash
git add README.md .gitlab-ci.yml
git commit -m "Start GitLab DevSecOps learning lab"
git push -u origin main
```

Then open GitLab:

```text
Build > Pipelines
```

Expected result:

- A pipeline appears for the commit.
- The `hello_pipeline` job runs.
- The job prints project, branch, commit, and pipeline details.

## 7. Fix Invalid CI YAML

If GitLab shows:

```text
jobs:hello_pipeline:script config should be a string or a nested array of strings
```

The likely cause is a shell command with a colon that YAML interprets as a map.
Quote the entire command:

```yaml
script:
  - 'echo "GitLab pipeline is alive."'
  - 'echo "Project: $CI_PROJECT_PATH"'
  - 'echo "Branch: $CI_COMMIT_BRANCH"'
  - 'echo "Commit: $CI_COMMIT_SHA"'
  - 'echo "Pipeline: $CI_PIPELINE_ID"'
```

Commit and push the fix:

```bash
git add .gitlab-ci.yml
git commit -m "Fix CI script YAML quoting"
git push
```

## 8. Lab 2: Security Scanning Branch

Start from the latest `main`:

```bash
git switch main
git pull --ff-only
git switch -c codex/lab-2-security-scanning
```

### What The Branch Name Means

`codex/lab-2-security-scanning` is a Git branch name, not a folder in the
project directory.

The slash is a naming convention that helps organize branches visually in
GitLab. It does not create a project folder named `codex`.

Think of branches as movable labels pointing to commits:

```text
main                          -> 80e2110
codex/lab-2-security-scanning -> cc574ed
```

When you run:

```bash
git push -u origin codex/lab-2-security-scanning
```

you are telling Git to:

1. Push the local branch named `codex/lab-2-security-scanning`.
2. Create the same branch name on GitLab if it does not already exist.
3. Set that GitLab branch as the upstream branch.

After the upstream is set, future pushes from that branch can usually be:

```bash
git push
```

Add GitLab security scanning templates to `.gitlab-ci.yml`:

```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.gitlab-ci.yml

stages:
  - verify
  - test
```

Stage and commit the security lab files:

```bash
git add .gitlab-ci.yml README.md .gitignore requirements.txt src/training_app.py
git commit -m "Add security scanning lab"
```

Push the branch:

```bash
git push -u origin codex/lab-2-security-scanning
```

Create a merge request:

```text
codex/lab-2-security-scanning -> main
```

Do not merge immediately. Inspect:

- `Build > Pipelines`
- Pipeline jobs
- `Secure > Vulnerability report`
- Merge request security widget

## 9. Reading The Merge Request Security Widget

After pushing the security scanning branch and opening a merge request, GitLab
can show a security widget on the MR overview.

Example:

```text
Security scanning detected 26 new potential vulnerabilities
1 critical, 15 high, and 10 others
```

This is the key DevSecOps lesson:

```text
Pipeline passed does not mean the change is secure.
```

It means the jobs ran successfully. Security scanners can complete successfully
and still report serious findings.

In this lab:

- `hello_pipeline` proves basic CI works.
- `semgrep-sast` performs Static Application Security Testing.
- `secret_detection` scans for committed credentials.
- `gemnasium-python-dependency_scanning` checks Python dependencies for known
  vulnerable packages.

The MR might still say `Ready to merge` because the current project rules allow
the merge. That does not mean the vulnerabilities are acceptable. It means
detection exists, but enforcement has not been configured yet.

When reviewing the MR security report, open a finding and inspect:

- File path
- Line number
- Severity
- Identifier, such as `bandit.B602`, `bandit.B608`, or a CVE
- Scanner type
- Remediation guidance

Typical findings in this lab:

- `bandit.B602`: command injection from shell execution.
- `bandit.B608`: SQL injection from string-built SQL.
- `bandit.B307`: eval injection from dynamically evaluated code.
- Dependency CVEs: known vulnerabilities from old package versions in
  `requirements.txt`.

Status meanings:

- `Needs triage`: GitLab found it, but no human has accepted, dismissed, or
  resolved it yet.
- `Detected`: the scanner reported the issue.
- `Resolved`: a later scan no longer finds the issue.
- `Dismissed`: a human decided not to act on the finding, ideally with a clear
  reason.

Do not merge this training MR until the lab asks you to. It intentionally
contains vulnerable code so you can practice triage and remediation.

## 10. Lab 3: Remediate Findings

Use the same merge request branch:

```bash
cd "/Users/ttenmattam/Documents/Learn Gitlab"
git status --short --branch
```

Expected branch:

```text
codex/lab-2-security-scanning
```

Lab 3 fixes the issues reported by Lab 2.

SAST remediation patterns:

- SQL injection: replace string-built SQL with parameterized SQL.
- Command injection: remove shell execution and avoid passing user input to a
  shell.
- Eval injection: remove `eval` and other dynamic code execution.
- Debug exposure: do not start Flask with `debug=True`.

Dependency remediation pattern:

- Replace vulnerable package pins with maintained versions.
- Prefer exact pins for reproducible training labs.
- Re-run dependency scanning after the update.

The dependency pins used in this lab were checked against PyPI on
May 20, 2026:

```text
Flask==3.1.3
Jinja2==3.1.6
Werkzeug==3.1.8
```

Stage, commit, and push the remediation:

```bash
git add README.md RUNBOOK.md requirements.txt src/training_app.py
git commit -m "Remediate training app vulnerabilities"
git push
```

Then return to the open merge request and inspect:

- Latest pipeline
- Security widget
- Security report
- Vulnerability statuses

Important lesson:

```text
Security remediation is a feedback loop.
```

The loop is:

1. Scanner detects a finding.
2. Engineer reads the finding in context.
3. Engineer changes code or dependencies.
4. Pipeline runs again.
5. GitLab updates the MR security report.

If a finding remains, repeat the loop. If a finding disappears from the latest
scan, GitLab can mark it as resolved.

## 11. Lab 4: Governance Controls

Lab 4 turns scanner output into workflow controls.

Goal:

```text
Risky changes should be visible, reviewed, and blocked when policy requires it.
```

### Protect `main`

In GitLab:

```text
Settings > Repository > Branch rules > main
```

Recommended learning-lab settings:

```text
Allowed to merge: Maintainers
Allowed to push and merge: No one
Allowed to force push: Off
Require approval from code owners: Off for now
```

Why:

- `Allowed to merge: Maintainers` lets maintainers merge reviewed MRs.
- `Allowed to push and merge: No one` prevents direct pushes to `main`.
- Force-push stays off so history cannot be rewritten casually.
- Code owner approval comes later, after adding `CODEOWNERS`.

### Add A Basic MR Approval Rule

In GitLab:

```text
Settings > Merge requests > Merge request approvals
```

Suggested rule:

```text
Rule name: Code review required
Approvals required: 1
Target branch: All protected branches
Approvers: a teammate, reviewer group, or maintainer group
```

Solo trial note:

If you are the only project member, avoid creating a hard rule that blocks MR
authors from approving their own changes unless another eligible approver exists.
That is realistic governance, but it can intentionally lock a solo lab.

### Add A Security Approval Policy

In GitLab:

```text
Secure > Policies > New policy > Merge request approval policy
```

Suggested policy:

```text
Name: Require security approval for high risk findings
Status: Enabled
Policy enforcement: Strictly enforced for blocking behavior, Warn mode for solo practice
Target branches: All protected branches
Scanners: SAST and Dependency Scanning
Severity: Critical and High
Threshold: More than 0 vulnerabilities
Action: Require 1 approval
Approver: security group, maintainer group, or eligible reviewer
```

Expected policy YAML shape:

```yaml
approval_policy:
  - name: Require security approval for high risk findings
    enabled: true
    enforcement_type: enforce
    rules:
      - type: scan_finding
        branch_type: protected
        scanners:
          - sast
          - dependency_scanning
        vulnerabilities_allowed: 0
        severity_levels:
          - critical
          - high
        vulnerability_states:
          - new_needs_triage
    actions:
      - type: require_approval
        approvals_required: 1
```

GitLab may create or update a security policy project and open a merge request
for the policy. Merge that policy MR to activate it.

### Test The Policy

Create a deliberately risky test branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-4-policy-test
```

Add the temporary file shown in the Lab Change Ledger, then push:

```bash
git add src/policy_test.py
git commit -m "Test security approval policy"
git push -u origin codex/lab-4-policy-test
```

Open an MR:

```text
codex/lab-4-policy-test -> main
```

Expected result:

- SAST reports a new high-risk finding.
- The MR shows a required approval or warning, depending on policy mode.
- The MR should not be merged as-is.

Close this test MR after observing the policy.

## 12. Lab 5: CODEOWNERS

Lab 5 maps repository files to accountable owners.

Goal:

```text
Changes to sensitive or owned paths should request review from the right people.
```

### Add CODEOWNERS

Create:

```text
.gitlab/CODEOWNERS
```

Current learning-lab ownership map:

```text
* @tejten

[Application]
/src/ @tejten
/requirements.txt @tejten

[CI/CD]
/.gitlab-ci.yml @tejten

[Documentation]
/README.md @tejten
/RUNBOOK.md @tejten
/.gitlab/CODEOWNERS @tejten
```

The first version used `@collibra-group`, but the test MR still showed
`Approval is optional`. For this solo lab, use your explicit username,
`@tejten`, so GitLab can resolve an eligible owner. Replace it with reviewer
groups when your lab has more people.

Valid owner examples:

```text
@username
@group-name
@group-name/subgroup-name
```

The owner must have access to the project. Invalid owners do not provide useful
approval coverage.

### Merge CODEOWNERS First

Recommended order:

1. Add `.gitlab/CODEOWNERS` in an MR.
2. Merge that MR.
3. Enable code owner approval on the protected branch.
4. Test with a separate branch.

This avoids creating a rule that requires code owner approval before the owner
map exists on `main`.

### Enable Code Owner Approval

In GitLab:

```text
Settings > Repository > Branch rules > main
```

Enable:

```text
Require approval from code owners
```

Keep:

```text
Allowed to push and merge: No one
Allowed to force push: Off
```

Solo trial note:

If you are the only project member and project settings prevent authors from
approving their own merge requests, this can intentionally block your test MR.
That is realistic in a team setting. For solo practice, use warn-mode policies
or add another eligible reviewer.

If GitLab shows:

```text
1 invalid rule has been approved automatically.
```

then GitLab found an approval rule but could not resolve it into a valid required
approval for this MR. In this solo lab, the common reason is that `@tejten` is
both the MR author and the only code owner while project settings prevent author
approval. The production fix is to add another eligible reviewer or group as a
code owner. The solo-lab workaround is to temporarily allow author approval or
invite a second test user.

### Test Code Owner Approval

After CODEOWNERS is merged and code owner approval is enabled, create a test
branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-5-codeowners-test
```

Make a small owned-path change, such as editing `src/training_app.py`:

```python
@app.route("/health")
def health():
    return {"status": "ok"}
```

Commit and push:

```bash
git add src/training_app.py
git commit -m "Test code owner approval"
git push -u origin codex/lab-5-codeowners-test
```

Open an MR:

```text
codex/lab-5-codeowners-test -> main
```

Expected result:

- GitLab identifies the file as owned by the CODEOWNERS rule.
- The MR requests approval from the owner.
- If code owner approval is required, the MR cannot merge until that approval is
  satisfied.
- If GitLab says `1 invalid rule has been approved automatically`, the ownership
  match exists but there is no eligible approver for the rule.

Close the test MR after observing the behavior, or remove the test route and
merge only if you want to keep the change.

Cleanup for a closed test MR:

```bash
git switch main
git pull --ff-only origin main
git branch -D codex/lab-5-codeowners-test
git push origin --delete codex/lab-5-codeowners-test
git fetch --prune
```

Lab 5 takeaway:

```text
CODEOWNERS turns repository structure into review routing.
```

Security policies answer "is this risky?" Code owners answer "who is accountable
for reviewing this area?"

## 13. Lab Change Ledger

Use this section when you want to repeat the labs from scratch or explain what
changed in each lab.

### How To Inspect Lab Changes With Git

Show the commit timeline:

```bash
git log --oneline --decorate --reverse
```

Show what a lab commit changed:

```bash
git show --stat COMMIT_SHA
git show COMMIT_SHA -- FILE_PATH
```

Compare two lab points:

```bash
git diff OLD_COMMIT..NEW_COMMIT -- FILE_PATH
```

### Lab 1: First Pipeline

Files created:

```text
README.md
.gitlab-ci.yml
```

Purpose:

```text
Prove that GitLab can create and run a pipeline from this repository.
```

Final `.gitlab-ci.yml` after the YAML quoting fix:

```yaml
stages:
  - verify

hello_pipeline:
  stage: verify
  image: alpine:3.20
  script:
    - 'echo "GitLab pipeline is alive."'
    - 'echo "Project: $CI_PROJECT_PATH"'
    - 'echo "Branch: $CI_COMMIT_BRANCH"'
    - 'echo "Commit: $CI_COMMIT_SHA"'
    - 'echo "Pipeline: $CI_PIPELINE_ID"'
```

Commands:

```bash
git add README.md .gitlab-ci.yml
git commit -m "Start GitLab DevSecOps learning lab"
git push -u origin main
```

YAML fix command:

```bash
git add .gitlab-ci.yml
git commit -m "Fix CI script YAML quoting"
git push
```

### Lab 2: Add Security Scanning

Files changed or created:

```text
.gitignore
.gitlab-ci.yml
README.md
requirements.txt
src/training_app.py
```

Purpose:

```text
Create a deliberately vulnerable branch so GitLab SAST and dependency scanning
have real findings to report in a merge request.
```

Security templates added to `.gitlab-ci.yml`:

```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/Dependency-Scanning.gitlab-ci.yml

stages:
  - verify
  - test
```

Vulnerable `requirements.txt` used for dependency scanning practice:

```text
Flask==0.12.2
Jinja2==2.10
Werkzeug==0.14.1
```

Vulnerable `src/training_app.py` used for SAST practice:

```python
"""Intentionally vulnerable training app for GitLab security scanning.

Do not deploy this app. It exists so SAST and dependency scanning have
real examples to detect during the DevSecOps learning labs.
"""

import sqlite3
import subprocess

from flask import Flask, request


app = Flask(__name__)


def find_customer(customer_id):
    conn = sqlite3.connect("customers.db")
    query = f"SELECT * FROM customers WHERE id = '{customer_id}'"
    return conn.execute(query).fetchall()


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)


@app.route("/debug")
def debug():
    expression = request.args.get("expr", "1 + 1")
    return str(eval(expression))


if __name__ == "__main__":
    app.run(debug=True)
```

Findings this version should produce:

```text
SQL injection
Command injection
Eval injection
Active debug code
Multiple dependency CVEs
```

Commands:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-2-security-scanning
git add .gitlab-ci.yml README.md .gitignore requirements.txt src/training_app.py
git commit -m "Add security scanning lab"
git push -u origin codex/lab-2-security-scanning
```

### Lab 3: Remediate Security Findings

Files changed:

```text
README.md
RUNBOOK.md
requirements.txt
src/training_app.py
```

Purpose:

```text
Replace vulnerable code and package versions, then let GitLab rescan the same
merge request to confirm the findings are gone.
```

Remediated `requirements.txt`:

```text
Flask==3.1.3
Jinja2==3.1.6
Werkzeug==3.1.8
```

Remediated `src/training_app.py`:

```python
"""Small training app used by the GitLab DevSecOps learning labs."""

import ipaddress
import sqlite3

from flask import Flask, request


app = Flask(__name__)


def find_customer(customer_id):
    with sqlite3.connect("customers.db") as conn:
        return conn.execute(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchall()


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return {"error": "host must be an IP address"}, 400

    return {"host": host, "status": "accepted"}


@app.route("/debug")
def debug():
    return {"debug": False, "status": "ok"}


if __name__ == "__main__":
    app.run()
```

Security changes:

```text
String-built SQL -> parameterized SQL
Shell command execution -> input validation and no shell execution
eval() -> static debug response
debug=True -> normal Flask startup
Vulnerable dependency pins -> maintained package versions
```

Validation commands:

```bash
python3 -m py_compile src/training_app.py
git diff --check
rg "shell=True|eval\\(|debug=True|subprocess|Flask==0|Jinja2==2|Werkzeug==0" \
  src requirements.txt README.md RUNBOOK.md
```

Commit and push:

```bash
git add README.md RUNBOOK.md requirements.txt src/training_app.py
git commit -m "Remediate training app vulnerabilities"
git push
```

Expected GitLab result:

```text
Security scanning detected no new potential vulnerabilities
```

### Lab 4: Governance Controls

Files changed locally during the policy test:

```text
src/policy_test.py
```

Purpose:

```text
Prove that branch protection and security approval policies can require review
for risky changes before they merge to main.
```

Temporary test file:

```python
from flask import request


def unsafe_debug_endpoint():
    expression = request.args.get("expr", "1 + 1")
    return str(eval(expression))
```

Commands to create the test branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-4-policy-test
git add src/policy_test.py
git commit -m "Test security approval policy"
git push -u origin codex/lab-4-policy-test
```

Expected GitLab result:

```text
SAST reports a new high-risk finding.
The merge request requires approval or warns according to policy mode.
```

Cleanup after observing the policy:

```bash
git switch main
git pull --ff-only origin main
git branch -D codex/lab-4-policy-test
git push origin --delete codex/lab-4-policy-test
git fetch --prune
```

Do not merge the policy test MR. It exists only to prove the policy behavior.

### Lab 5: CODEOWNERS

Files changed or created:

```text
.gitlab/CODEOWNERS
README.md
RUNBOOK.md
```

Purpose:

```text
Map repository paths to accountable owners and require owner review for protected
branches.
```

CODEOWNERS file:

```text
# GitLab DevSecOps Learning Lab code ownership.
#
# Owners must be valid GitLab users or groups with access to this project.
# @tejten is used for the solo lab; replace it with teams as your lab grows.

* @tejten

[Application]
/src/ @tejten
/requirements.txt @tejten

[CI/CD]
/.gitlab-ci.yml @tejten

[Documentation]
/README.md @tejten
/RUNBOOK.md @tejten
/.gitlab/CODEOWNERS @tejten
```

Commands to add CODEOWNERS:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-5-codeowners
git add .gitlab/CODEOWNERS README.md RUNBOOK.md
git commit -m "Add code owner rules"
git push -u origin codex/lab-5-codeowners
```

Expected GitLab result:

```text
The MR shows CODEOWNERS changes.
After merge and branch-rule configuration, future owned-path changes require
code owner approval.
```

Commands to test code owner approval:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-5-codeowners-test
git add src/training_app.py
git commit -m "Test code owner approval"
git push -u origin codex/lab-5-codeowners-test
```

Cleanup after observing the test MR:

```bash
git switch main
git pull --ff-only origin main
git branch -D codex/lab-5-codeowners-test
git push origin --delete codex/lab-5-codeowners-test
git fetch --prune
```

## 14. Repeatability Notes

For every future lab, record:

- Branch name.
- Files changed.
- Exact code snippet or configuration added.
- Commit message.
- Push command.
- Expected GitLab pipeline or security result.
- Cleanup command if the lab creates a temporary branch.

Prefer recording lab instructions in this runbook rather than adding historical
comments inside application source files. Source comments should explain current
code behavior; the runbook should explain the learning journey.

## 15. Useful Daily Git Commands

Check current branch and file state:

```bash
git status --short --branch
```

See recent commits:

```bash
git log --oneline --decorate -5
```

See unstaged changes:

```bash
git diff
```

See staged changes:

```bash
git diff --cached
```

Check for whitespace problems before committing:

```bash
git diff --check
```

Push current branch:

```bash
git push
```

Push a new branch and set upstream:

```bash
git push -u origin BRANCH_NAME
```

## 16. What To Remember

- A local commit does not run a GitLab pipeline until it is pushed.
- GitLab creates pipelines from `.gitlab-ci.yml`.
- YAML validity is checked before jobs are created.
- Security scanners are usually most useful in merge requests.
- A branch is a Git pointer, not a visible project folder.
- A passing pipeline means the automation ran successfully, not that the code is
  automatically secure.
- `Ready to merge` means current project rules allow the merge. It does not mean
  the security findings are resolved.
- Remediation is not done when the code is edited. It is done when the next scan
  confirms the finding is gone or intentionally accepted.
- CODEOWNERS routes reviews based on files and directories.
- Code owner rules need eligible approvers. A rule with only the MR author as
  owner can become invalid when author self-approval is disabled.
- Repeatable labs need a change ledger: files touched, exact snippets, commands,
  expected GitLab result, and cleanup steps.
- Keep risky training code isolated and clearly marked as intentionally unsafe.
