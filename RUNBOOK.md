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

## 9. Useful Daily Git Commands

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

## 10. What To Remember

- A local commit does not run a GitLab pipeline until it is pushed.
- GitLab creates pipelines from `.gitlab-ci.yml`.
- YAML validity is checked before jobs are created.
- Security scanners are usually most useful in merge requests.
- Keep risky training code isolated and clearly marked as intentionally unsafe.
