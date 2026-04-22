"""SOTA Fleet Launch Protocol: launch a repo by path (start.ps1)."""

import subprocess
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

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
    repo = Path(repo_path)
    if not repo.is_dir():
        return {"status": "error", "message": "Path not found"}
    start_ps1 = repo / "start.ps1"
    if not start_ps1.is_file():
        return {"status": "error", "message": "start.ps1 not found"}
    subprocess.Popen(  # noqa: S603
        [  # noqa: S607
            "powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "start.ps1",
        ],
        cwd=str(repo),
    )
    return {
        "status": "success",
        "message": f"Launched {repo.name}",
    }
