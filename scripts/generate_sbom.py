"""Generate training SBOM and provenance artifacts for the GitLab labs."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"
DOCKERFILE = ROOT / "Dockerfile"
OUT_DIR = ROOT / "evidence"
SBOM_PATH = OUT_DIR / "training-sbom.cdx.json"
PROVENANCE_PATH = OUT_DIR / "build-provenance.json"


def read_pinned_requirements() -> list[dict[str, str]]:
    components = []

    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        requirement = line.strip()
        if not requirement or requirement.startswith("#"):
            continue

        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^#\s]+)", requirement)
        if not match:
            raise ValueError(f"Only pinned requirements are supported: {requirement}")

        name, version = match.groups()
        purl = f"pkg:pypi/{name.lower()}@{version}"
        components.append(
            {
                "type": "library",
                "bom-ref": purl,
                "name": name,
                "version": version,
                "purl": purl,
            }
        )

    return components


def read_base_image() -> dict[str, str]:
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("FROM "):
            image = stripped.split()[1]
            name, _, version = image.partition(":")
            return {
                "type": "container",
                "bom-ref": f"container-base:{image}",
                "name": name,
                "version": version or "latest",
                "properties": [
                    {"name": "dockerfile.from", "value": image},
                ],
            }

    raise ValueError("Dockerfile does not contain a FROM instruction")


def env(name: str, default: str = "local") -> str:
    return os.environ.get(name, default)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    app_ref = "application:gitlab-devsecops-training-app"
    components = read_pinned_requirements()
    components.append(read_base_image())

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "component": {
                "type": "application",
                "bom-ref": app_ref,
                "name": env("CI_PROJECT_PATH", ROOT.name),
                "version": env("CI_COMMIT_SHA", "local"),
            },
        },
        "components": components,
        "dependencies": [
            {
                "ref": app_ref,
                "dependsOn": [component["bom-ref"] for component in components],
            }
        ],
    }

    provenance = {
        "generated_at": timestamp,
        "project": env("CI_PROJECT_PATH", ROOT.name),
        "project_url": env("CI_PROJECT_URL", ""),
        "branch": env("CI_COMMIT_REF_NAME", "local"),
        "commit_sha": env("CI_COMMIT_SHA", "local"),
        "pipeline_id": env("CI_PIPELINE_ID", "local"),
        "container_image": {
            "repository": env("CI_REGISTRY_IMAGE", ""),
            "tag": env("CI_COMMIT_SHA", "local"),
        },
        "sbom": str(SBOM_PATH.relative_to(ROOT)),
    }

    SBOM_PATH.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    PROVENANCE_PATH.write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {SBOM_PATH.relative_to(ROOT)}")
    print(f"Wrote {PROVENANCE_PATH.relative_to(ROOT)}")
    print(f"Recorded {len(components)} components")


if __name__ == "__main__":
    main()
