"""SOTA Fleet Launch Protocol: launch a repo by path (start.ps1)."""

import logging
import os
import subprocess

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class LaunchRequest(BaseModel):
    repo_path: str


ALLOWED_PREFIXES = ("d:/dev/repos", "c:/users/sandr")


@router.post("/fleet/launch")
async def fleet_launch(launch_req: LaunchRequest) -> dict:
    """SOTA Fleet Launch Protocol: run start.ps1 in the given repo if path is allowed."""
    repo_path = launch_req.repo_path.strip()
    if not repo_path:
        return {"status": "error", "message": "repo_path is required"}
    normalized = repo_path.lower().replace("\\", "/")
    if not any(normalized.startswith(p) for p in ALLOWED_PREFIXES):
        return {"status": "error", "message": "Forbidden path"}
    if not os.path.exists(repo_path):
        return {"status": "error", "message": "Path not found"}
    start_ps1 = os.path.join(repo_path, "start.ps1")
    if not os.path.exists(start_ps1):
        return {"status": "error", "message": "start.ps1 not found"}
    subprocess.Popen(
        [
            "powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "start.ps1",
        ],
        cwd=repo_path,
    )
    return {
        "status": "success",
        "message": f"Launched {os.path.basename(repo_path)}",
    }
