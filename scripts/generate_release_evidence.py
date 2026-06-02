"""Generate release evidence artifacts for tag-based GitLab releases."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "evidence"
HTML_PATH = OUT_DIR / "release-evidence.html"
JSON_PATH = OUT_DIR / "release-evidence.json"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def html_row(label: str, value: str) -> str:
    return (
        "<tr>"
        f"<th>{html.escape(label)}</th>"
        f"<td><code>{html.escape(value)}</code></td>"
        "</tr>"
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    project_url = env("CI_PROJECT_URL", "")
    tag = env("CI_COMMIT_TAG", "local-tag")
    pipeline_url = env("CI_PIPELINE_URL", "")

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": env("CI_PROJECT_PATH", ROOT.name),
        "project_url": project_url,
        "release_tag": tag,
        "commit_sha": env("CI_COMMIT_SHA", "local"),
        "pipeline_id": env("CI_PIPELINE_ID", "local"),
        "pipeline_url": pipeline_url,
        "job_id": env("CI_JOB_ID", "local"),
        "container_image": {
            "repository": env("CI_REGISTRY_IMAGE", ""),
            "tag": env("CI_COMMIT_SHA", "local"),
        },
        "artifact_links": {
            "release_evidence": (
                f"{project_url}/-/jobs/artifacts/{tag}/file/evidence/release-evidence.html"
                "?job=generate_release_evidence"
            )
            if project_url
            else "",
            "sbom": (
                f"{project_url}/-/jobs/artifacts/{tag}/file/evidence/training-sbom.cdx.json"
                "?job=generate_sbom"
            )
            if project_url
            else "",
            "build_provenance": (
                f"{project_url}/-/jobs/artifacts/{tag}/file/evidence/build-provenance.json"
                "?job=generate_sbom"
            )
            if project_url
            else "",
        },
    }

    rows = [
        html_row("Generated at", record["generated_at"]),
        html_row("Project", record["project"]),
        html_row("Release tag", record["release_tag"]),
        html_row("Commit", record["commit_sha"]),
        html_row("Pipeline", record["pipeline_id"]),
        html_row("Pipeline URL", record["pipeline_url"]),
        html_row("Job", record["job_id"]),
        html_row(
            "Container image",
            f"{record['container_image']['repository']}:{record['container_image']['tag']}",
        ),
        html_row("SBOM link", record["artifact_links"]["sbom"]),
        html_row("Build provenance link", record["artifact_links"]["build_provenance"]),
    ]

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Release Evidence</title>
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
  <h1>Release Evidence</h1>
  <p>This tag-based release record ties a version tag to the pipeline, commit, container image, SBOM, and build provenance.</p>
  <table>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""

    JSON_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    HTML_PATH.write_text(page, encoding="utf-8")

    print(f"Wrote {HTML_PATH.relative_to(ROOT)}")
    print(f"Wrote {JSON_PATH.relative_to(ROOT)}")
    print(f"Release tag: {tag}")


if __name__ == "__main__":
    main()
