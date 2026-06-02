"""Generate deployment evidence artifacts for the GitLab labs."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "evidence"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def html_row(label: str, value: str) -> str:
    return (
        "<tr>"
        f"<th>{html.escape(label)}</th>"
        f"<td><code>{html.escape(value)}</code></td>"
        "</tr>"
    )


def artifact_url(project_url: str, job_id: str, basename: str) -> str:
    if not project_url or job_id == "local":
        return ""

    return f"{project_url}/-/jobs/{job_id}/artifacts/file/evidence/{basename}.html"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    basename = env("DEPLOYMENT_RECORD_BASENAME", "deployment-record")
    title = env("DEPLOYMENT_RECORD_TITLE", "Deployment Evidence")
    description = env(
        "DEPLOYMENT_RECORD_DESCRIPTION",
        "This lab creates a GitLab environment record without deploying to cloud infrastructure.",
    )
    deployment_type = env("DEPLOYMENT_TYPE", "simulated-deployment")

    html_path = OUT_DIR / f"{basename}.html"
    json_path = OUT_DIR / f"{basename}.json"
    job_id = env("CI_JOB_ID", "local")
    project_url = env("CI_PROJECT_URL", "")

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": env("CI_PROJECT_PATH", ROOT.name),
        "project_url": project_url,
        "branch": env("CI_COMMIT_REF_NAME", "local"),
        "commit_sha": env("CI_COMMIT_SHA", "local"),
        "pipeline_id": env("CI_PIPELINE_ID", "local"),
        "job_id": job_id,
        "environment_name": env("CI_ENVIRONMENT_NAME", "local"),
        "environment_slug": env("CI_ENVIRONMENT_SLUG", "local"),
        "environment_url": env(
            "CI_ENVIRONMENT_URL",
            artifact_url(project_url, job_id, basename),
        ),
        "container_image": {
            "repository": env("CI_REGISTRY_IMAGE", ""),
            "tag": env("CI_COMMIT_SHA", "local"),
        },
        "deployment_type": deployment_type,
    }

    rows = [
        html_row("Generated at", record["generated_at"]),
        html_row("Project", record["project"]),
        html_row("Branch", record["branch"]),
        html_row("Commit", record["commit_sha"]),
        html_row("Pipeline", record["pipeline_id"]),
        html_row("Job", record["job_id"]),
        html_row("Environment", record["environment_name"]),
        html_row("Environment URL", record["environment_url"]),
        html_row("Deployment type", record["deployment_type"]),
        html_row(
            "Container image",
            f"{record['container_image']['repository']}:{record['container_image']['tag']}",
        ),
    ]

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      color: #1f2937;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      margin: 2rem;
      max-width: 900px;
    }}

    table {{
      border-collapse: collapse;
      width: 100%;
    }}

    th,
    td {{
      border-bottom: 1px solid #d1d5db;
      padding: 0.75rem;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      width: 12rem;
    }}

    code {{
      overflow-wrap: anywhere;
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(description)}</p>
  <table>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""

    json_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(page, encoding="utf-8")

    print(f"Wrote {html_path.relative_to(ROOT)}")
    print(f"Wrote {json_path.relative_to(ROOT)}")
    print(f"Environment: {record['environment_name']}")


if __name__ == "__main__":
    main()
