"""FFmpeg-based media management portmanteau tool for Plex."""

import asyncio
import json
from pathlib import Path
from typing import Literal

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


@mcp.tool()
async def plex_ffmpeg_mgr(
    operation: Literal["sync_audio", "probe", "revert", "extract_subtitles", "sync_subtitles", "set_aspect"],
    media_key: str,
    offset_seconds: float = 0.0,
    aspect_ratio: str = None,
    stream_index: int = 0,
    reencode: bool = False,
) -> str:
    """Industrial-grade FFmpeg management tool for Plex media.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates low-level media repair and inspection tasks that require system-level
    FFmpeg binaries. This avoids tool explosion while providing powerful repair
    capabilities for broken rips or sync-drifted media.

    OPERATIONS:
    - sync_audio: Adjust audio/video synchronization by shifting the audio track.
      Creates a .bak file of the original. Uses a stream-copy approach (zero quality loss).
    - probe: Retrieve detailed technical metadata (codecs, tracks, streams) using ffprobe.
    - revert: Restore the original media file from a .bak file created by repair operations.
    - extract_subtitles: Extract an internal subtitle stream to a sidecar file (.srt, .ass).
      Uses language tagging from Plex if available.
    - sync_subtitles: Shift the timing of ALL internal subtitle tracks simultaneously.
    - set_aspect: Correct the Display Aspect Ratio (DAR) of the video.

    Args:
        operation: The action to perform.
        media_key: The Plex ratingKey (id) of the media item.
        offset_seconds: For sync_audio and sync_subtitles, delay in seconds.
            Positive (+) delays (later). Negative (-) advances (earlier).
        aspect_ratio: Target ratio for set_aspect (e.g., "16:9", "4:3", "2.35:1").
        stream_index: For extract_subtitles, the index of the subtitle stream (0-based).
        reencode: For set_aspect, if True, performs a full re-encode to fix baked-in AR.
            If False (default), only modifies metadata header (instant).

    Returns:
        Structured JSON response with success status, action details, and result/error.
    """
    plex = await _get_plex_service()
    try:
        # Resolve file path
        analysis = await plex.get_media_analysis(media_key)
        if not analysis or "media" not in analysis or not analysis["media"]:
            return json.dumps(
                {
                    "success": False,
                    "operation": operation,
                    "error": f"Media not found or analysis failed for key: {media_key}",
                },
                indent=2,
            )

        # Take first part of first media version for repair
        media_item = analysis["media"][0]
        if not media_item.get("parts"):
            return json.dumps(
                {
                    "success": False,
                    "operation": operation,
                    "error": "No file parts found associated with this media item",
                },
                indent=2,
            )

        source_file_str = media_item["parts"][0]["file"]
        source_path = Path(source_file_str)

        if not source_path.exists():
            return json.dumps(
                {
                    "success": False,
                    "operation": operation,
                    "error": f"File not found on local filesystem: {source_path}. Ensure Plex server and MCP are on the same node.",
                },
                indent=2,
            )

        if operation == "probe":
            return await _handle_probe(source_path)
        elif operation == "sync_audio":
            return await _handle_sync_audio(source_path, offset_seconds, plex, media_key)
        elif operation == "sync_subtitles":
            return await _handle_sync_subtitles(source_path, offset_seconds, plex, media_key)
        elif operation == "revert":
            return await _handle_revert(source_path, plex, media_key)
        elif operation == "set_aspect":
            return await _handle_set_aspect(source_path, aspect_ratio, reencode, plex, media_key)
        elif operation == "extract_subtitles":
            return await _handle_extract_subtitles(source_path, stream_index, plex, media_key)

        return json.dumps(
            {"success": False, "operation": operation, "error": f"Unsupported operation: {operation}"}, indent=2
        )

    except Exception as e:
        logger.error(f"plex_ffmpeg_mgr error: {e!s}")
        return json.dumps(
            {"success": False, "operation": operation, "error": f"Internal error during FFmpeg operation: {e!s}"},
            indent=2,
        )
    finally:
        await plex.close()


async def _handle_probe(file_path: Path) -> str:
    """Execute ffprobe and return JSON metadata."""
    cmd = [FFPROBE_PATH, "-v", "error", "-show_format", "-show_streams", "-print_format", "json", str(file_path)]

    logger.debug(f"Probing file: {file_path}")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return json.dumps(
            {"success": False, "operation": "probe", "error": f"ffprobe failed: {stderr.decode().strip()}"}, indent=2
        )

    return json.dumps({"success": True, "operation": "probe", "result": json.loads(stdout.decode())}, indent=2)


async def _handle_sync_audio(file_path: Path, offset: float, plex: PlexService, media_key: str) -> str:
    """Perform audio sync repair using offset headers."""
    if offset == 0:
        return json.dumps(
            {
                "success": False,
                "operation": "sync_audio",
                "error": "Offset must be a non-zero value for sync_audio adjustment",
            },
            indent=2,
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


async def _handle_sync_subtitles(file_path: Path, offset: float, plex: PlexService, media_key: str) -> str:
    """Shift timing for all internal subtitle tracks simultaneously."""
    if offset == 0:
        return json.dumps(
            {"success": False, "operation": "sync_subtitles", "error": "Offset must be a non-zero value"}, indent=2
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


async def _handle_set_aspect(file_path: Path, aspect: str, reencode: bool, plex: PlexService, media_key: str) -> str:
    """Change Display Aspect Ratio (metadata or re-encode)."""
    if not aspect:
        return json.dumps(
            {"success": False, "operation": "set_aspect", "error": "aspect_ratio parameter is required (e.g. 16:9)"},
            indent=2,
        )

    temp_path = file_path.with_suffix(f".ar_tmp{file_path.suffix}")
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    if reencode:
        # Full re-encode to fix stubborn issues (slow)
        cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-aspect", aspect, str(temp_path)]
    else:
        # Fast metadata-only fix
        cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-aspect", aspect, "-c", "copy", str(temp_path)]

    return await _process_and_rotate(cmd, temp_path, file_path, bak_path, "set_aspect", plex, media_key)


async def _handle_extract_subtitles(file_path: Path, stream_idx: int, plex: PlexService, media_key: str) -> str:
    """Extract a specific internal sub track to a sidecar file."""
    probe_raw = await _handle_probe(file_path)
    probe_data = json.loads(probe_raw)

    if not probe_data["success"]:
        return probe_raw

    subs = [s for s in probe_data["result"].get("streams", []) if s.get("codec_type") == "subtitle"]
    if stream_idx >= len(subs):
        return json.dumps(
            {
                "success": False,
                "operation": "extract_subtitles",
                "error": f"Subtitle stream index {stream_idx} out of range. Found {len(subs)} streams.",
            },
            indent=2,
        )

    target_stream = subs[stream_idx]
    codec = target_stream.get("codec_name", "srt")

    # Map common codecs to extensions
    ext_map = {"subrip": "srt", "mov_text": "srt", "ass": "ass", "dvbsub": "srt", "pgssub": "sup"}
    ext = ext_map.get(codec, "srt")

    # Try to get language tag from metadata
    lang = target_stream.get("tags", {}).get("language", "und")

    output_name = f"{file_path.stem}.{lang}.{ext}"
    output_path = file_path.parent / output_name

    cmd = [FFMPEG_PATH, "-y", "-i", str(file_path), "-map", f"0:s:{stream_idx}", str(output_path)]

    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return json.dumps(
            {
                "success": False,
                "operation": "extract_subtitles",
                "error": f"Extraction failed: {stderr.decode().strip()}",
            },
            indent=2,
        )

    return json.dumps(
        {
            "success": True,
            "operation": "extract_subtitles",
            "result": {"output_file": str(output_path), "stream_index": stream_idx, "codec": codec, "language": lang},
        },
        indent=2,
    )


async def _process_and_rotate(
    cmd: list, temp_path: Path, file_path: Path, bak_path: Path, op_name: str, plex: PlexService, media_key: str
) -> str:
    """Generic helper for FFmpeg operations that modify the source file."""
    logger.info(f"Executing {op_name} for {file_path}...")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        if temp_path.exists():
            temp_path.unlink()
        return json.dumps(
            {"success": False, "operation": op_name, "error": f"FFmpeg processing failed: {stderr.decode().strip()}"},
            indent=2,
        )

    try:
        # Atomic file rotation
        if bak_path.exists():
            bak_path.unlink()

        file_path.rename(bak_path)
        temp_path.rename(file_path)

        # Trigger Plex re-analysis via plexapi
        logger.info(f"Triggering Plex analysis for media_key: {media_key}")
        await plex._run_in_executor(lambda: plex.server.fetchItem(int(media_key)).analyze())

        return json.dumps(
            {
                "success": True,
                "operation": op_name,
                "result": {
                    "file": str(file_path),
                    "backup_created": str(bak_path),
                    "message": f"Operation {op_name} completed successfully.",
                },
            },
            indent=2,
        )
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return json.dumps({"success": False, "operation": op_name, "error": f"Rotation failed: {e!s}"}, indent=2)


async def _handle_revert(file_path: Path, plex: PlexService, media_key: str) -> str:
    """Restore the .bak file to the original location."""
    bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")

    if not bak_path.exists():
        return json.dumps(
            {"success": False, "operation": "revert", "error": f"No backup file (.bak) found for {file_path.name}"},
            indent=2,
        )

    try:
        # Delete the repaired file and restore the backup
        if file_path.exists():
            file_path.unlink()
        bak_path.rename(file_path)

        # Trigger Plex re-analysis to restore metadata state
        await plex._run_in_executor(lambda: plex.server.fetchItem(int(media_key)).analyze())

        return json.dumps(
            {
                "success": True,
                "operation": "revert",
                "result": {"file": str(file_path), "message": "Reverted to original backup successfully."},
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "operation": "revert", "error": f"Revert operation failed: {e!s}"}, indent=2
        )
