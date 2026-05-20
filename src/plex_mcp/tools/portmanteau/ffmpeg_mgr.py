"""FFmpeg-based media management portmanteau tool for Plex."""

import asyncio
import json
from pathlib import Path
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.plex_service import PlexService
from ...utils import get_logger

logger = get_logger(__name__)

# Mandatory SOTA paths for FFmpeg/FFprobe
FFMPEG_PATH = "C:\\ffmpeg\\ffmpeg.exe"
FFPROBE_PATH = "C:\\ffmpeg\\ffprobe.exe"


async def _get_plex_service() -> PlexService:
    """Helper to get and connect Plex service."""
    plex = PlexService()
    await plex.connect()
    return plex


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def plex_ffmpeg_mgr(
    operation: Annotated[
        Literal["sync_audio", "probe", "revert", "extract_subtitles", "sync_subtitles", "set_aspect"],
        Field(description="Operation to perform."),
    ],
    media_key: Annotated[str, Field(description="Plex ratingKey of the media item.")],
    offset_seconds: Annotated[float, Field(description="Delay in seconds for sync operations.")] = 0.0,
    aspect_ratio: Annotated[str | None, Field(description="Target aspect ratio (e.g. 16:9).")] = None,
    stream_index: Annotated[int, Field(description="Stream index for subtitle extraction.")] = 0,
    reencode: Annotated[bool, Field(description="Full re-encode for set_aspect.")] = False,
) -> ToolResult:
    """Industrial-grade FFmpeg management tool for Plex media.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates low-level media repair and inspection tasks that require system-level
    FFmpeg binaries. This avoids tool explosion while providing powerful repair
    capabilities for broken rips or sync-drifted media.

    ## Return Format
    {"success": bool, "data": dict, "message": str}

    ## Examples
    await plex_ffmpeg_mgr(operation="probe", media_key="12345")
    await plex_ffmpeg_mgr(operation="sync_audio", media_key="12345", offset_seconds=-1.5)
    """
    plex = await _get_plex_service()
    try:
        analysis = await plex.get_media_analysis(media_key)
        if not analysis or "media" not in analysis or not analysis["media"]:
            return ToolResult(
                content={
                    "success": False,
                    "operation": operation,
                    "error": f"Media not found or analysis failed for key: {media_key}",
                }
            )

        media_item = analysis["media"][0]
        if not media_item.get("parts"):
            return ToolResult(
                content={
                    "success": False,
                    "operation": operation,
                    "error": "No file parts found associated with this media item",
                }
            )

        source_file_str = media_item["parts"][0]["file"]
        source_path = Path(source_file_str)

        if not source_path.exists():
            return ToolResult(
                content={
                    "success": False,
                    "operation": operation,
                    "error": f"File not found on local filesystem: {source_path}. Ensure Plex server and MCP are on the same node.",
                }
            )

        if operation == "probe":
            return await _handle_probe(source_path)
        if operation == "sync_audio":
            return await _handle_sync_audio(source_path, offset_seconds, plex, media_key)
        if operation == "sync_subtitles":
            return await _handle_sync_subtitles(source_path, offset_seconds, plex, media_key)
        if operation == "revert":
            return await _handle_revert(source_path, plex, media_key)
        if operation == "set_aspect":
            return await _handle_set_aspect(source_path, aspect_ratio, reencode, plex, media_key)
        if operation == "extract_subtitles":
            return await _handle_extract_subtitles(source_path, stream_index, plex, media_key)

        return ToolResult(
            content={
                "success": False,
                "operation": operation,
                "error": f"Unsupported operation: {operation}",
            }
        )

    except Exception as e:
        logger.exception(f"plex_ffmpeg_mgr error: {e!s}")
        return ToolResult(
            content={
                "success": False,
                "operation": operation,
                "error": f"Internal error during FFmpeg operation: {e!s}",
            }
        )
    finally:
        await plex.close()


async def _handle_probe(file_path: Path) -> ToolResult:
    """Execute ffprobe and return metadata."""
    cmd = [FFPROBE_PATH, "-v", "error", "-show_format", "-show_streams", "-print_format", "json", str(file_path)]

    logger.debug(f"Probing file: {file_path}")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return ToolResult(
            content={
                "success": False,
                "operation": "probe",
                "error": f"ffprobe failed: {stderr.decode().strip()}",
            }
        )

    return ToolResult(
        content={
            "success": True,
            "operation": "probe",
            "result": json.loads(stdout.decode()),
        }
    )


async def _handle_sync_audio(file_path: Path, offset: float, plex: PlexService, media_key: str) -> ToolResult:
    """Perform audio sync repair using offset headers."""
    if offset == 0:
        return ToolResult(
            content={
                "success": False,
                "operation": "sync_audio",
                "error": "Offset must be a non-zero value for sync_audio adjustment",
            }
        )

    temp_path = file_path.with_suffix(f".sync_tmp{file_path.suffix}")
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(file_path),
        "-itsoffset",
        str(offset),
        "-i",
        str(file_path),
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-c",
        "copy",
        str(temp_path),
    ]

    return await _process_and_rotate(cmd, temp_path, file_path, bak_path, "sync_audio", plex, media_key)


async def _handle_sync_subtitles(file_path: Path, offset: float, plex: PlexService, media_key: str) -> ToolResult:
    """Shift timing for all internal subtitle tracks simultaneously."""
    if offset == 0:
        return ToolResult(
            content={
                "success": False,
                "operation": "sync_subtitles",
                "error": "Offset must be a non-zero value",
            }
        )

    temp_path = file_path.with_suffix(f".subs_tmp{file_path.suffix}")
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(file_path),
        "-itsoffset",
        str(offset),
        "-i",
        str(file_path),
        "-map",
        "0:v",
        "-map",
        "0:a",
        "-map",
        "1:s",
        "-c",
        "copy",
        str(temp_path),
    ]

    return await _process_and_rotate(cmd, temp_path, file_path, bak_path, "sync_subtitles", plex, media_key)


async def _handle_set_aspect(
    file_path: Path, aspect: str, reencode: bool, plex: PlexService, media_key: str
) -> ToolResult:
    """Change Display Aspect Ratio (metadata or re-encode)."""
    if not aspect:
        return ToolResult(
            content={
                "success": False,
                "operation": "set_aspect",
                "error": "aspect_ratio parameter is required (e.g. 16:9)",
            }
        )

    temp_path = file_path.with_suffix(f".ar_tmp{file_path.suffix}")
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    if reencode:
        cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-aspect", aspect, str(temp_path)]
    else:
        cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-aspect", aspect, "-c", "copy", str(temp_path)]

    return await _process_and_rotate(cmd, temp_path, file_path, bak_path, "set_aspect", plex, media_key)


async def _handle_extract_subtitles(file_path: Path, stream_idx: int, plex: PlexService, media_key: str) -> ToolResult:
    """Extract a specific internal sub track to a sidecar file."""
    probe_result = await _handle_probe(file_path)

    if not probe_result.content["success"]:
        return probe_result

    probe_data = probe_result.content
    subs = [s for s in probe_data.get("result", {}).get("streams", []) if s.get("codec_type") == "subtitle"]
    if stream_idx >= len(subs):
        return ToolResult(
            content={
                "success": False,
                "operation": "extract_subtitles",
                "error": f"Subtitle stream index {stream_idx} out of range. Found {len(subs)} streams.",
            }
        )

    target_stream = subs[stream_idx]
    codec = target_stream.get("codec_name", "srt")
    ext_map = {"subrip": "srt", "mov_text": "srt", "ass": "ass", "dvbsub": "srt", "pgssub": "sup"}
    ext = ext_map.get(codec, "srt")
    lang = target_stream.get("tags", {}).get("language", "und")
    output_name = f"{file_path.stem}.{lang}.{ext}"
    output_path = file_path.parent / output_name

    cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-map", f"0:s:{stream_idx}", str(output_path)]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return ToolResult(
            content={
                "success": False,
                "operation": "extract_subtitles",
                "error": f"Extraction failed: {stderr.decode().strip()}",
            }
        )

    return ToolResult(
        content={
            "success": True,
            "operation": "extract_subtitles",
            "result": {"output_file": str(output_path), "stream_index": stream_idx, "codec": codec, "language": lang},
        }
    )


async def _process_and_rotate(
    cmd: list, temp_path: Path, file_path: Path, bak_path: Path, op_name: str, plex: PlexService, media_key: str
) -> ToolResult:
    """Generic helper for FFmpeg operations that modify the source file."""
    logger.info(f"Executing {op_name} for {file_path}...")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        if temp_path.exists():
            temp_path.unlink()
        return ToolResult(
            content={
                "success": False,
                "operation": op_name,
                "error": f"FFmpeg processing failed: {stderr.decode().strip()}",
            }
        )

    try:
        if bak_path.exists():
            bak_path.unlink()

        file_path.rename(bak_path)
        temp_path.rename(file_path)

        logger.info(f"Triggering Plex analysis for media_key: {media_key}")
        await plex._run_in_executor(lambda: plex.server.fetchItem(int(media_key)).analyze())

        return ToolResult(
            content={
                "success": True,
                "operation": op_name,
                "result": {
                    "file": str(file_path),
                    "backup_created": str(bak_path),
                    "message": f"Operation {op_name} completed successfully.",
                },
            }
        )
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return ToolResult(
            content={
                "success": False,
                "operation": op_name,
                "error": f"Rotation failed: {e!s}",
            }
        )


async def _handle_revert(file_path: Path, plex: PlexService, media_key: str) -> ToolResult:
    """Restore the .bak file to the original location."""
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    if not bak_path.exists():
        return ToolResult(
            content={
                "success": False,
                "operation": "revert",
                "error": f"No backup file (.bak) found for {file_path.name}",
            }
        )

    try:
        if file_path.exists():
            file_path.unlink()
        bak_path.rename(file_path)

        await plex._run_in_executor(lambda: plex.server.fetchItem(int(media_key)).analyze())

        return ToolResult(
            content={
                "success": True,
                "operation": "revert",
                "result": {"file": str(file_path), "message": "Reverted to original backup successfully."},
            }
        )
    except Exception as e:
        return ToolResult(
            content={
                "success": False,
                "operation": "revert",
                "error": f"Revert operation failed: {e!s}",
            }
        )
