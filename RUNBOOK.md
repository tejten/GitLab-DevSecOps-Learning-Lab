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

### Step 1: Merge The Clean MR

Only do this after the MR says:

```text
Security scanning detected no new potential vulnerabilities
```

In the merge request, select `Merge`.

If `Delete source branch` is selected, GitLab deletes the remote feature branch
after the merge. That is normal. The code lands on `main`; the temporary branch
is no longer needed.

Sync your local repository afterward:

```bash
cd "/Users/ttenmattam/Documents/Learn Gitlab"
git switch main
git pull --ff-only origin main
```

Optional local cleanup:

```bash
git branch -d codex/lab-2-security-scanning
```

### Step 2: Protect `main`

GitLab now configures protected branches under branch rules.

In GitLab:

```text
Settings > Repository > Branch rules
```

Open or create the rule for:

```text
main
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
- Code owner approval comes later, after we add `CODEOWNERS`.

Current GitLab docs note that `Allowed to push and merge` must be explicitly set
to `No one` if you want to prevent direct pushes.

### Step 3: Add A Basic MR Approval Rule

In GitLab:

```text
Settings > Merge requests > Merge request approvals
```

Add an approval rule:

```text
Rule name: Code review required
Approvals required: 1
Target branch: All protected branches
Approvers: a teammate or reviewer group
```

Solo trial note:

If you are the only project member, do not create a hard approval rule that only
you can satisfy while also preventing authors from approving their own MRs. That
can create an intentionally blocked lab setup. In a real organization, use a
reviewer group such as security, platform, or maintainers.

Concept:

```text
Approval rules make review explicit.
Branch protection makes the rule matter for important branches.
```

### Step 4: Add A Security Approval Policy

Security approval policies are Ultimate-tier controls that require approval when
scanner findings meet policy conditions.

In GitLab:

```text
Secure > Policies > New policy > Merge request approval policy
```

Create a policy like:

```text
Name: Require security approval for high risk findings
Status: Enabled

IF Security Scan from SAST and Dependency Scanning finds more than 0
Critical or High vulnerabilities in an open merge request targeting
All protected branches

THEN require approval from 1 approver
```

Choose an eligible approver or group. In a real team, this is usually a security
or application-owner group.

GitLab creates or updates a security policy project and opens a merge request
for the policy. Merge that policy MR to activate the policy.

Important behavior:

- Security approval policies apply to protected target branches.
- Scanner jobs must produce security reports for GitLab to evaluate the policy.
- If GitLab cannot evaluate the policy safely, it may require approval instead
  of silently allowing the MR.

### Step 5: Test The Policy With A Bad Branch

After the policy is active, create a test branch from `main`:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-4-policy-test
```

Add a deliberately risky file:

```python
# src/policy_test.py
from flask import request


def unsafe_debug_endpoint():
    expression = request.args.get("expr", "1 + 1")
    return str(eval(expression))
```

Commit and push:

```bash
git add src/policy_test.py
git commit -m "Test security approval policy"
git push -u origin codex/lab-4-policy-test
```

Open a merge request:

```text
codex/lab-4-policy-test -> main
```

Expected result:

- SAST reports a new finding.
- The MR shows a required security approval.
- The MR should not be casually mergeable until the policy requirement is met
  or the finding is fixed.

Close this test MR after observing the policy. It exists only to prove the
control works.

### Step 6: Fix Or Close The Test MR

To fix it, remove the risky file:

```bash
git rm src/policy_test.py
git commit -m "Remove policy test vulnerability"
git push
```

Then wait for the pipeline and confirm the security approval requirement clears.

If you are done with the demonstration, close the MR instead of merging it.

Lab 4 takeaway:

```text
DevSecOps maturity is not just scanner coverage. It is scanner coverage plus
branch protection, review rules, and policies that turn findings into enforceable
workflow.
```

## 12. Useful Daily Git Commands

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

## 13. What To Remember

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
- Branch protection prevents important branches from being changed casually.
- Approval rules and security policies turn review expectations into platform
  behavior.
- Keep risky training code isolated and clearly marked as intentionally unsafe.
