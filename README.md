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
