# GitLab DevSecOps Learning Lab

This repository is a hands-on learning path for GitLab DevSecOps.

## Learning Goal

Build one concept at a time:

1. Git and GitLab project basics.
2. CI/CD pipelines with stages, jobs, runners, variables, caches, and artifacts.
3. Shift-left security with SAST, secret detection, dependency scanning, container scanning, and DAST.
4. Merge request controls with protected branches, approvals, CODEOWNERS, and security policies.
5. Release and deployment workflows with environments, review apps, and rollback practices.
6. Vulnerability triage, remediation, dashboards, compliance, and auditability.

## Lab 1

The first pipeline proves that GitLab can run a job for this project.

After pushing this repository to GitLab, open:

- Build > Pipelines
- The latest pipeline
- The `hello_pipeline` job logs

You should see the commit, branch, and pipeline ID printed by the job.

## Lab 2

The second lab turns basic CI into DevSecOps by adding security scanners:

- Static Application Security Testing (SAST) scans source code for vulnerable patterns.
- Secret detection scans repository content for accidentally committed credentials.
- Dependency scanning checks open source packages against known vulnerability data.

The `src/training_app.py` file is intentionally unsafe. Do not deploy it. It exists so
the scanners have realistic issues to report.

After pushing this branch, open a merge request and inspect:

- Build > Pipelines
- Secure > Vulnerability report
- The merge request security widget

## Lab 3

The third lab remediates the findings from Lab 2:

- SQL injection is fixed with a parameterized query.
- Command injection is fixed by removing shell execution.
- Eval injection is fixed by removing dynamic evaluation.
- Debug mode is disabled for normal app startup.
- Vulnerable dependency pins are updated to current maintained releases.

After pushing the remediation commit to the same branch, GitLab reruns the
pipeline and updates the merge request security report.

## Lab 4

The fourth lab moves from scanning to governance:

- Protect `main` so changes flow through merge requests.
- Add merge request approval expectations.
- Add a merge request approval policy for high-risk security findings.
- Test the policy with a deliberately risky branch.

This is where DevSecOps shifts from "we can detect risk" to "the platform can
enforce review before risky changes land."

## Lab 5

The fifth lab adds code ownership:

- Add `.gitlab/CODEOWNERS`.
- Map application, CI/CD, and documentation files to valid GitLab owners.
- Enable code owner approval on the protected `main` branch.
- Test that changing owned files requires the right reviewer.

This is where review becomes tied to file ownership, not just a generic approval.

## Lab 6

The sixth lab adds container artifact security:

- Add a Dockerfile for the Flask training app.
- Build and push an image to the GitLab Container Registry.
- Add GitLab container scanning.
- Scan the image that would be deployed, not only the source code.

This is where DevSecOps shifts from "is the source safe?" to "is the packaged
runtime artifact safe?"

## Lab 7

The seventh lab remediates container findings:

- Move the image to a current Python slim Bookworm tag.
- Apply available Debian package updates during the image build.
- Upgrade Python packaging tools that scanners often flag inside images.
- Re-run container scanning and compare findings against Lab 6.

This is where container security becomes a maintenance loop instead of a
one-time scan.

## Lab 8

The eighth lab compares an alternate container base image:

- Switch from Debian slim to Alpine.
- Rebuild and rescan the container image.
- Compare total findings and severity distribution.
- Discuss image-size, compatibility, and security tradeoffs.

This is where container hardening becomes evidence-driven rather than assuming
one base image is always best.
