"""Generate a review-environment deployment record for the GitLab labs."""

from __future__ import annotations

import os

from generate_deployment_record import main


os.environ.setdefault("DEPLOYMENT_RECORD_BASENAME", "review-deployment")
os.environ.setdefault("DEPLOYMENT_RECORD_TITLE", "Review Deployment Evidence")
os.environ.setdefault(
    "DEPLOYMENT_RECORD_DESCRIPTION",
    "This lab creates a GitLab environment record without deploying to cloud infrastructure.",
)
os.environ.setdefault("DEPLOYMENT_TYPE", "simulated-review-environment")
os.environ.setdefault("CI_ENVIRONMENT_NAME", "review/local")
os.environ.setdefault("CI_ENVIRONMENT_SLUG", "review-local")


if __name__ == "__main__":
    main()
