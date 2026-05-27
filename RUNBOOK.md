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

## 13. Lab 6: Container Build And Scanning

Lab 6 scans the deployable artifact: the container image.

Goal:

```text
Build the app into an image, push it to the GitLab Container Registry, and scan
that image for vulnerabilities.
```

### Add Container Files

Create:

```text
Dockerfile
.dockerignore
```

The Dockerfile uses:

- `python:3.12-slim` as the base image.
- Exact Python dependencies from `requirements.txt`.
- A non-root `app` user.
- Flask on port `5000`.

The `.dockerignore` file keeps Git metadata, caches, and local files out of the
build context.

### Add Container Scanning

Add GitLab's container scanning template:

```yaml
include:
  - template: Jobs/Container-Scanning.gitlab-ci.yml
```

Add a `build` stage between `verify` and `test`:

```yaml
stages:
  - verify
  - build
  - test
```

Build and push the image with rootless BuildKit:

```yaml
build_container_image:
  stage: build
  image:
    name: moby/buildkit:rootless
    entrypoint: [""]
  variables:
    BUILDKITD_FLAGS: --oci-worker-no-process-sandbox
  before_script:
    - mkdir -p ~/.docker
    - 'echo "{\"auths\":{\"$CI_REGISTRY\":{\"username\":\"$CI_REGISTRY_USER\",\"password\":\"$CI_REGISTRY_PASSWORD\"}}}" > ~/.docker/config.json'
  script:
    - |
      buildctl-daemonless.sh build \
        --frontend dockerfile.v0 \
        --local context=. \
        --local dockerfile=. \
        --output type=image,name="$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA",push=true
```

Point container scanning at that image:

```yaml
variables:
  CI_APPLICATION_REPOSITORY: "$CI_REGISTRY_IMAGE"
  CI_APPLICATION_TAG: "$CI_COMMIT_SHA"
  CS_DISABLE_LANGUAGE_VULNERABILITY_SCAN: "false"

container_scanning:
  needs:
    - build_container_image
```

`CS_DISABLE_LANGUAGE_VULNERABILITY_SCAN: "false"` asks the scanner to include
language package vulnerabilities found inside the image, not only operating
system package vulnerabilities.

### Update CODEOWNERS

Add container files to ownership:

```text
[Containers]
/Dockerfile @tejten
/.dockerignore @tejten
```

### Run The Lab

Create the branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-6-container-scanning
```

Commit and push:

```bash
git add Dockerfile .dockerignore .gitlab-ci.yml .gitlab/CODEOWNERS README.md RUNBOOK.md src/__init__.py
git commit -m "Add container image scanning lab"
git push -u origin codex/lab-6-container-scanning
```

Open an MR:

```text
codex/lab-6-container-scanning -> main
```

Expected pipeline jobs:

```text
hello_pipeline
build_container_image
container_scanning
semgrep-sast
secret_detection
gemnasium-python-dependency_scanning
```

Expected GitLab areas to inspect:

- `Build > Pipelines`
- `Deploy > Container registry`
- MR security widget
- `Secure > Vulnerability report`

### Troubleshooting

If `build_container_image` fails:

- Confirm the project Container Registry is enabled.
- Confirm GitLab CI variables `CI_REGISTRY`, `CI_REGISTRY_USER`, and
  `CI_REGISTRY_PASSWORD` are available in the job log.
- Check whether the runner supports rootless BuildKit.

If `container_scanning` reports no image:

- Confirm `build_container_image` pushed `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA`.
- Confirm `CI_APPLICATION_REPOSITORY` is `$CI_REGISTRY_IMAGE`.
- Confirm `CI_APPLICATION_TAG` is `$CI_COMMIT_SHA`.

Lab 6 takeaway:

```text
Source scanning catches risky code. Container scanning checks the runtime image
that would actually be deployed.
```

## 14. Lab 7: Container Remediation

Lab 7 reduces container findings from Lab 6.

Goal:

```text
Treat the container image as a maintained artifact by updating the base image,
OS packages, and Python packaging tools, then compare scan results.
```

### What Lab 6 Showed

The Lab 6 MR security report showed:

```text
Container scanning detected at least 25 new potential vulnerabilities
0 critical, 4 high, and 21 others
```

The important lesson:

```text
Clean source scans do not guarantee a clean runtime image.
```

Container findings often come from:

- Base image OS packages.
- Language tooling bundled in the image, such as `pip`.
- Packages installed transitively by the base image.
- Images that are not rebuilt after upstream patches are published.

### Remediation Strategy

Update the Dockerfile from:

```dockerfile
FROM python:3.12-slim
```

to:

```dockerfile
FROM python:3.13.13-slim-bookworm
```

Then update packages during the image build:

```dockerfile
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir --upgrade \
        pip==26.1.1 \
        setuptools==82.0.1 \
        wheel==0.47.0 \
    && python -m pip install --no-cache-dir -r requirements.txt
```

The pinned tool versions were checked on May 26, 2026:

```text
pip==26.1.1
setuptools==82.0.1
wheel==0.47.0
```

### Run The Lab

Create a remediation branch from the Lab 6 branch:

```bash
git switch codex/lab-6-container-scanning
git switch -c codex/lab-7-container-remediation
```

Commit and push:

```bash
git add Dockerfile README.md RUNBOOK.md
git commit -m "Remediate container image baseline"
git push -u origin codex/lab-7-container-remediation
```

Open an MR:

```text
codex/lab-7-container-remediation -> main
```

Expected result:

- The container image is rebuilt.
- `container_scanning` runs again.
- The MR security widget shows whether the count changed.

Compare against Lab 6:

```text
Lab 6 baseline: at least 25 container vulnerabilities, 4 high.
Lab 7 result: 17 container vulnerabilities, 2 critical, 0 high, and 15 others.
```

Lab 7 improved the total count and removed high findings, but two critical
findings remained. That is a realistic remediation outcome: a change can reduce
risk without eliminating it.

### If Findings Remain

Remaining findings are normal. Container remediation is iterative.

Next options:

- Wait for patched upstream base images and rebuild.
- Try a smaller or hardened runtime image.
- Remove unnecessary runtime packages.
- Add an allowlist only with a documented risk acceptance reason.
- Use a stricter deployment policy for critical/high container findings.

Lab 7 takeaway:

```text
Container security is not solved once. Images must be rebuilt, rescanned, and
maintained as upstream base images and package advisories change.
```

## 15. Lab 8: Compare An Alpine Base Image

Lab 8 compares an alternate base image strategy.

Goal:

```text
Change the base image family, rebuild, rescan, and compare evidence instead of
assuming a smaller image is automatically safer.
```

### Strategy

Update the Dockerfile from:

```dockerfile
FROM python:3.13.13-slim-bookworm
```

to:

```dockerfile
FROM python:3.13.13-alpine3.22
```

Replace Debian package updates:

```dockerfile
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*
```

with Alpine package updates:

```dockerfile
RUN apk upgrade --no-cache
```

Alpine tradeoff:

```text
Alpine images are usually smaller and have a different package set, but they use
musl libc instead of glibc. Some Python packages with native extensions can need
extra build dependencies or behave differently.
```

This lab app uses pure Python Flask dependencies, so Alpine is a reasonable
comparison.

### Run The Lab

Create a branch from Lab 7:

```bash
git switch codex/lab-7-container-remediation
git switch -c codex/lab-8-alpine-image
```

Commit and push:

```bash
git add Dockerfile README.md RUNBOOK.md
git commit -m "Compare Alpine container base"
git push -u origin codex/lab-8-alpine-image
```

Open an MR:

```text
codex/lab-8-alpine-image -> main
```

Expected result:

- The image rebuilds with Alpine.
- Container scanning reports a different finding set.
- You compare the result against Lab 7.

Comparison table:

```text
Lab 6 Debian baseline: at least 25 container vulnerabilities, 4 high.
Lab 7 updated Debian: 17 container vulnerabilities, 2 critical, 0 high.
Lab 8 Alpine: 0 new container vulnerabilities.
```

GitLab listed the Debian-image findings from Lab 6 and Lab 7 as fixed after the
Alpine image scan. This does not mean Alpine is always better. It means this app
and dependency set produced a cleaner scan with the Alpine base at the time of
the lab.

Lab 8 takeaway:

```text
Base image choice is a risk tradeoff. Compare scan results, compatibility, image
size, patch cadence, and operational support before standardizing.
```

## 16. Lab 9: Dynamic Application Security Testing

Lab 9 adds DAST: Dynamic Application Security Testing.

Goal:

```text
Run the application in CI and scan the live HTTP surface from the outside, the
way a browser or attacker would interact with it.
```

### What DAST Adds

The earlier labs scan different layers:

- SAST scans source code.
- Secret detection scans committed content.
- Dependency scanning scans package manifests.
- Container scanning scans the built image.

DAST scans a running web application. For this lab, the pipeline builds the
Flask container image, starts that image as a CI service named `app`, and points
the GitLab DAST analyzer at:

```text
http://app:5000
```

### Add DAST To CI

Add the GitLab DAST template:

```yaml
include:
  - template: Security/DAST.gitlab-ci.yml
```

Add a DAST stage:

```yaml
stages:
  - verify
  - build
  - test
  - dast
```

Configure the `dast` job to wait for the image build, run the built image as a
service, and scan the service URL:

```yaml
dast:
  needs:
    - build_container_image
  services:
    - name: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
      alias: app
  variables:
    DAST_TARGET_URL: "http://app:5000"
    DAST_FULL_SCAN: "false"
    DAST_TARGET_CHECK_TIMEOUT: "120"
```

Important details:

- `build_container_image` creates and pushes the container image.
- The `services` block starts that image next to the DAST analyzer job.
- The service alias `app` becomes the hostname inside the CI network.
- `DAST_TARGET_URL` tells DAST which running app to scan.
- `DAST_FULL_SCAN: "false"` keeps this first lab passive and faster.

### Run The Lab

Create a branch from Lab 8:

```bash
git switch codex/lab-8-alpine-image
git switch -c codex/lab-9-dast
```

Commit and push:

```bash
git add .gitlab-ci.yml README.md RUNBOOK.md
git commit -m "Add DAST lab"
git push -u origin codex/lab-9-dast
```

Open an MR:

```text
codex/lab-9-dast -> main
```

Expected result:

- `build_container_image` builds and pushes the app image.
- `dast` starts the app image as a service.
- DAST scans `http://app:5000`.
- Results appear in the pipeline security report and MR Reports tab.

### Troubleshooting

If the pipeline says the DAST template cannot be found, replace:

```yaml
- template: Security/DAST.gitlab-ci.yml
```

with:

```yaml
- template: DAST.gitlab-ci.yml
```

GitLab has used both forms across documentation and template examples.

If DAST cannot connect to the target:

- Confirm the Dockerfile runs Flask on `--host=0.0.0.0`.
- Confirm the service alias is `app`.
- Confirm `DAST_TARGET_URL` is `http://app:5000`.
- Confirm `build_container_image` completed successfully before `dast`.
- Increase `DAST_TARGET_CHECK_TIMEOUT` if the app starts slowly.

If DAST finds no vulnerabilities, that is not a failure. This lab is about
proving that GitLab can scan a running app. Future labs can add authentication,
active scans, review apps, or intentionally vulnerable routes.

Lab 9 takeaway:

```text
DAST validates the deployed behavior of a web application. It complements
source, dependency, and container scanning because runtime behavior can reveal
issues that static analysis cannot.
```

## 17. Lab 10: Remediate DAST Security Headers

Lab 10 fixes the first DAST findings from Lab 9.

Goal:

```text
Add browser-facing security headers to every response, reduce avoidable server
metadata, and rerun DAST to confirm the live HTTP surface improved.
```

### What The Lab 9 Findings Mean

DAST found:

- `Missing X-Content-Type-Options: nosniff`
- `Server header exposes version information`
- `Content-Security-Policy analysis`

These are runtime HTTP findings. They are visible in live responses, which is
why SAST, dependency scanning, and container scanning did not report them.

### Add Response Security Headers

In `src/training_app.py`, add a shared header map:

```python
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'none'"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=()",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}
```

Apply those headers to every Flask response:

```python
@app.after_request
def add_security_headers(response):
    response.headers.update(SECURITY_HEADERS)
    return response
```

For this training app, also prevent the Flask/Werkzeug development server from
advertising its exact Werkzeug and Python versions:

```python
WSGIRequestHandler.server_version = "training-app"
WSGIRequestHandler.sys_version = ""
```

In a production system, this part usually belongs in the real app server,
ingress controller, load balancer, or reverse proxy configuration.

### Run The Lab

Create a branch from Lab 9:

```bash
git switch codex/lab-9-dast
git switch -c codex/lab-10-dast-remediation
```

Commit and push:

```bash
git add src/training_app.py README.md RUNBOOK.md
git commit -m "Remediate DAST security headers"
git push -u origin codex/lab-10-dast-remediation
```

Open an MR:

```text
codex/lab-10-dast-remediation -> main
```

Expected result:

- SAST remains clean.
- Dependency scanning remains clean.
- Container scanning remains clean.
- DAST should no longer report missing `X-Content-Type-Options`.
- DAST should no longer see Werkzeug/Python version details in the `Server`
  header.
- CSP analysis should improve, or become an accepted informational note
  depending on GitLab's DAST rule behavior.

### Local Header Check

Start the app locally:

```bash
python3 -m flask --app src.training_app run --host 127.0.0.1 --port 5001
```

In another terminal, inspect the headers:

```bash
curl -s -D - http://127.0.0.1:5001/health -o /tmp/lab10-health.out
```

Expected headers include:

```text
Server: training-app
Content-Security-Policy: default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), geolocation=(), microphone=()
```

Lab 10 takeaway:

```text
DAST findings become most useful when they create a remediation loop: scan the
running app, change runtime behavior, rescan, and record what improved.
```

## 18. Lab 11: SBOM And Build Evidence Artifacts

Lab 11 adds supply-chain evidence artifacts.

Goal:

```text
Generate a CycloneDX SBOM and a small provenance file so every pipeline can
answer: what did we build, from which commit, with which dependencies, and where
is the resulting container image?
```

### Why This Matters

Security scanners tell you whether known risks were detected. SBOM and
provenance artifacts help answer a different audit question:

```text
What exactly was inside this build, and which pipeline produced it?
```

For this training repo, the SBOM records:

- Pinned Python dependencies from `requirements.txt`.
- The Docker base image from `Dockerfile`.
- The project and commit that produced the SBOM.

The provenance file records:

- Project path.
- Branch.
- Commit SHA.
- Pipeline ID.
- Container image repository and tag.

### Add The SBOM Generator

Add `scripts/generate_sbom.py`.

The script:

- Reads pinned dependencies from `requirements.txt`.
- Reads the `FROM` image from `Dockerfile`.
- Writes `evidence/training-sbom.cdx.json`.
- Writes `evidence/build-provenance.json`.

The generated files are ignored locally because CI publishes them as artifacts:

```gitignore
/evidence/
```

### Publish Artifacts In GitLab CI

Add an `evidence` stage:

```yaml
stages:
  - verify
  - evidence
  - build
  - test
  - dast
```

Add the SBOM job:

```yaml
generate_sbom:
  stage: evidence
  image: python:3.13-alpine
  script:
    - python scripts/generate_sbom.py
    - python -m json.tool evidence/training-sbom.cdx.json > /tmp/training-sbom.validated.json
    - python -m json.tool evidence/build-provenance.json > /tmp/build-provenance.validated.json
  artifacts:
    when: always
    expire_in: 1 week
    paths:
      - evidence/training-sbom.cdx.json
      - evidence/build-provenance.json
    reports:
      cyclonedx:
        - evidence/training-sbom.cdx.json
```

Important details:

- `paths` makes both files downloadable from the job.
- `reports: cyclonedx` tells GitLab this artifact is an SBOM report.
- The validation commands fail the job if either JSON file is malformed.

### Run The Lab

Create a branch from Lab 10:

```bash
git switch codex/lab-10-dast-remediation
git switch -c codex/lab-11-sbom-artifacts
```

Commit and push:

```bash
git add .gitignore .gitlab-ci.yml scripts/generate_sbom.py README.md RUNBOOK.md
git commit -m "Add SBOM evidence artifacts"
git push -u origin codex/lab-11-sbom-artifacts
```

Open an MR:

```text
codex/lab-11-sbom-artifacts -> main
```

Expected result:

- The `generate_sbom` job runs in the `evidence` stage.
- The job publishes `training-sbom.cdx.json`.
- The job publishes `build-provenance.json`.
- GitLab accepts the CycloneDX report artifact.

### Inspect The Artifacts

Open:

```text
Build > Pipelines > latest pipeline > generate_sbom
```

Then use the artifact download button to inspect:

```text
evidence/training-sbom.cdx.json
evidence/build-provenance.json
```

The SBOM should include:

```text
Flask
Jinja2
Werkzeug
python:3.13.13-alpine3.22
```

Lab 11 takeaway:

```text
DevSecOps is not only about blocking bad changes. It is also about producing
evidence that lets you explain what was built, where it came from, and what it
contained.
```

## 19. Lab Change Ledger

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

### Lab 6: Container Build And Scanning

Files changed or created:

```text
Dockerfile
.dockerignore
.gitlab-ci.yml
.gitlab/CODEOWNERS
README.md
RUNBOOK.md
src/__init__.py
```

Purpose:

```text
Build the Flask app as a container image, push it to the GitLab Container
Registry, and scan the image with GitLab container scanning.
```

Dockerfile:

```dockerfile
FROM python:3.12-slim

ENV FLASK_APP=src.training_app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER app

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
```

Container scanning CI additions:

```yaml
include:
  - template: Jobs/Container-Scanning.gitlab-ci.yml

variables:
  CI_APPLICATION_REPOSITORY: "$CI_REGISTRY_IMAGE"
  CI_APPLICATION_TAG: "$CI_COMMIT_SHA"
  CS_DISABLE_LANGUAGE_VULNERABILITY_SCAN: "false"

stages:
  - verify
  - build
  - test

build_container_image:
  stage: build
  image:
    name: moby/buildkit:rootless
    entrypoint: [""]
  variables:
    BUILDKITD_FLAGS: --oci-worker-no-process-sandbox
  before_script:
    - mkdir -p ~/.docker
    - 'echo "{\"auths\":{\"$CI_REGISTRY\":{\"username\":\"$CI_REGISTRY_USER\",\"password\":\"$CI_REGISTRY_PASSWORD\"}}}" > ~/.docker/config.json'
  script:
    - |
      buildctl-daemonless.sh build \
        --frontend dockerfile.v0 \
        --local context=. \
        --local dockerfile=. \
        --output type=image,name="$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA",push=true

container_scanning:
  needs:
    - build_container_image
```

Commands:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/lab-6-container-scanning
git add Dockerfile .dockerignore .gitlab-ci.yml .gitlab/CODEOWNERS README.md RUNBOOK.md src/__init__.py
git commit -m "Add container image scanning lab"
git push -u origin codex/lab-6-container-scanning
```

Expected GitLab result:

```text
The pipeline builds and pushes a container image.
The container_scanning job scans that pushed image.
The MR security widget reports container image findings, if any.
```

### Lab 7: Container Remediation

Files changed:

```text
Dockerfile
README.md
RUNBOOK.md
```

Purpose:

```text
Reduce container findings by updating the base image, applying OS package
updates, and pinning current Python packaging tools inside the image.
```

Dockerfile changes:

```diff
- FROM python:3.12-slim
+ FROM python:3.13.13-slim-bookworm
```

```dockerfile
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir --upgrade \
        pip==26.1.1 \
        setuptools==82.0.1 \
        wheel==0.47.0 \
    && python -m pip install --no-cache-dir -r requirements.txt
```

Commands:

```bash
git switch codex/lab-6-container-scanning
git switch -c codex/lab-7-container-remediation
git add Dockerfile README.md RUNBOOK.md
git commit -m "Remediate container image baseline"
git push -u origin codex/lab-7-container-remediation
```

Expected GitLab result:

```text
GitLab rebuilds the container image and reruns container_scanning.
Compare the finding count and severity distribution with Lab 6.
```

Observed result:

```text
Lab 6 baseline: at least 25 container vulnerabilities, 4 high.
Lab 7 result: 17 container vulnerabilities, 2 critical, 0 high, and 15 others.
```

### Lab 8: Compare Alpine Container Base

Files changed:

```text
Dockerfile
README.md
RUNBOOK.md
```

Purpose:

```text
Compare the container scan result from a Debian slim base image with an Alpine
base image.
```

Dockerfile changes:

```diff
- FROM python:3.13.13-slim-bookworm
+ FROM python:3.13.13-alpine3.22
```

```diff
- RUN apt-get update \
-     && apt-get upgrade -y \
-     && rm -rf /var/lib/apt/lists/*
+ RUN apk upgrade --no-cache
```

Commands:

```bash
git switch codex/lab-7-container-remediation
git switch -c codex/lab-8-alpine-image
git add Dockerfile README.md RUNBOOK.md
git commit -m "Compare Alpine container base"
git push -u origin codex/lab-8-alpine-image
```

Expected GitLab result:

```text
GitLab rebuilds the container image and reruns container_scanning.
Record whether the finding count and severity profile improve or regress.
```

Observed result:

```text
Container scanning detected no new potential vulnerabilities.
Previously reported Debian-image findings were shown as fixed.
```

### Lab 9: Dynamic Application Security Testing

Files changed:

```text
.gitlab-ci.yml
README.md
RUNBOOK.md
```

Purpose:

```text
Run the Flask app as a CI service and scan the live HTTP surface with GitLab
DAST.
```

CI additions:

```yaml
include:
  - template: Security/DAST.gitlab-ci.yml

stages:
  - verify
  - build
  - test
  - dast

dast:
  needs:
    - build_container_image
  services:
    - name: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
      alias: app
  variables:
    DAST_TARGET_URL: "http://app:5000"
    DAST_FULL_SCAN: "false"
    DAST_TARGET_CHECK_TIMEOUT: "120"
```

Commands:

```bash
git switch codex/lab-8-alpine-image
git switch -c codex/lab-9-dast
git add .gitlab-ci.yml README.md RUNBOOK.md
git commit -m "Add DAST lab"
git push -u origin codex/lab-9-dast
```

Expected GitLab result:

```text
The pipeline builds the app image, starts it as the app service, runs DAST
against http://app:5000, and publishes DAST results in the security report.
```

Observed result:

```text
DAST reached the running Flask app and detected 3 new potential vulnerabilities:

- Low: Missing X-Content-Type-Options: nosniff
- Low: Server header exposes version information
- Info: Content-Security-Policy analysis

SAST, dependency scanning, container scanning, and secret detection reported no
new potential vulnerabilities in the same MR.
```

Interpretation:

```text
This is a successful DAST lab. The scanner tested the live HTTP response and
found missing or noisy browser-facing security headers. These are runtime/web
configuration issues, not source-code vulnerabilities.
```

Natural next remediation lab:

```text
Add security headers to the Flask app, reduce avoidable response metadata, and
rerun DAST to confirm the findings are resolved or intentionally accepted.
```

### Lab 10: Remediate DAST Security Headers

Files changed:

```text
src/training_app.py
README.md
RUNBOOK.md
```

Purpose:

```text
Fix the first runtime HTTP findings produced by DAST.
```

Application changes:

```python
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'none'"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=()",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}

WSGIRequestHandler.server_version = "training-app"
WSGIRequestHandler.sys_version = ""


@app.after_request
def add_security_headers(response):
    response.headers.update(SECURITY_HEADERS)
    return response
```

Commands:

```bash
git switch codex/lab-9-dast
git switch -c codex/lab-10-dast-remediation
git add src/training_app.py README.md RUNBOOK.md
git commit -m "Remediate DAST security headers"
git push -u origin codex/lab-10-dast-remediation
```

Local verification:

```bash
python3 -m flask --app src.training_app run --host 127.0.0.1 --port 5001
curl -s -D - http://127.0.0.1:5001/health -o /tmp/lab10-health.out
```

Expected GitLab result:

```text
DAST should show the missing nosniff header and server version disclosure as
fixed or absent in the new MR security report.
```

Observed result:

```text
GitLab reported no new potential security vulnerabilities.

DAST detected no new potential vulnerabilities and marked the Lab 9 findings as
fixed:

- Low: Missing X-Content-Type-Options: nosniff
- Low: Server header exposes version information
- Info: Content-Security-Policy analysis

SAST, dependency scanning, container scanning, and secret detection also reported
no new potential vulnerabilities.
```

### Lab 11: SBOM And Build Evidence Artifacts

Files changed:

```text
.gitignore
.gitlab-ci.yml
scripts/generate_sbom.py
README.md
RUNBOOK.md
```

Purpose:

```text
Generate and publish supply-chain evidence artifacts from the pipeline.
```

CI additions:

```yaml
stages:
  - verify
  - evidence
  - build
  - test
  - dast

generate_sbom:
  stage: evidence
  image: python:3.13-alpine
  script:
    - python scripts/generate_sbom.py
    - python -m json.tool evidence/training-sbom.cdx.json > /tmp/training-sbom.validated.json
    - python -m json.tool evidence/build-provenance.json > /tmp/build-provenance.validated.json
  artifacts:
    when: always
    expire_in: 1 week
    paths:
      - evidence/training-sbom.cdx.json
      - evidence/build-provenance.json
    reports:
      cyclonedx:
        - evidence/training-sbom.cdx.json
```

Commands:

```bash
git switch codex/lab-10-dast-remediation
git switch -c codex/lab-11-sbom-artifacts
git add .gitignore .gitlab-ci.yml scripts/generate_sbom.py README.md RUNBOOK.md
git commit -m "Add SBOM evidence artifacts"
git push -u origin codex/lab-11-sbom-artifacts
```

Local verification:

```bash
python3 scripts/generate_sbom.py
python3 -m json.tool evidence/training-sbom.cdx.json
python3 -m json.tool evidence/build-provenance.json
```

Expected GitLab result:

```text
The generate_sbom job publishes downloadable SBOM and provenance artifacts, and
GitLab ingests the CycloneDX SBOM report.
```

Observed result:

```text
Pipeline #2557129666 passed with 8 jobs.

The generate_sbom job completed successfully in the evidence stage and published
downloadable artifacts.

Downloaded artifacts included:

- evidence/training-sbom.cdx.json
- evidence/build-provenance.json

The provenance artifact recorded the project URL, branch, commit SHA, pipeline
ID, container image repository, and image tag.

The SBOM artifact recorded the application component, Python dependencies, and
Docker base image:

- Flask 3.1.3
- Jinja2 3.1.6
- Werkzeug 3.1.8
- python:3.13.13-alpine3.22
```

## 20. Repeatability Notes

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

## 21. Useful Daily Git Commands

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

## 22. What To Remember

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
- Container scanning checks the packaged image, including the base image and
  installed packages, not just source code.
- Container remediation is iterative: rebuild from maintained bases, patch
  packages, rescan, and document remaining risk.
- Smaller base images are not automatically safer. Compare scan findings and
  runtime compatibility before standardizing.
- DAST scans the running app over HTTP, so it needs a reachable target URL.
- A CI service alias is a pipeline hostname, not a project folder.
- Passive DAST is a safer first step; active scans are more aggressive and
  should target test environments.
- HTTP security headers are runtime behavior. They are usually verified by DAST
  or HTTP integration tests, not by dependency scanners.
- Do not rely on the Flask development server for production. In real systems,
  app server and reverse proxy headers need their own hardening.
- An SBOM is an inventory of components. It helps audit what was present in a
  build, but it does not prove by itself that the build is secure.
- Provenance ties evidence to a source revision and pipeline run.
- GitLab job artifacts are part of the audit trail. Download and inspect them
  when learning a new scanner or report type.
- Repeatable labs need a change ledger: files touched, exact snippets, commands,
  expected GitLab result, and cleanup steps.
- Keep risky training code isolated and clearly marked as intentionally unsafe.
