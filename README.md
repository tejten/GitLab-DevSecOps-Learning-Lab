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
