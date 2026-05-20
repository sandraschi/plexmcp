"""Image proxy API."""

import logging
import os

import httpx
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_plex_config():
    base_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    token = os.getenv("PLEX_TOKEN")
    return base_url, token


@router.get("/{path:path}")
async def proxy_image(
    path: str,
    width: int | None = None,
    height: int | None = None,
    min_size: int | None = Query(None, alias="minSize"),
):
    """Proxy image requests to Plex."""
    return await _proxy_image(path, width, height, min_size)


async def _proxy_image(
    path: str,
    width: int | None = None,
    height: int | None = None,
    min_size: int | None = None,
):
    """Shared image proxy logic."""
    base_url, token = _get_plex_config()
    if not token:
        return Response(status_code=500, content="PLEX_TOKEN not set")

    # If asking for transcode
    if path == "transcode":
        # This needs careful handling, usually Plex handles /photo/:/transcode
        # We might receive query params that we need to pass
        pass

    # Construct Plex URL
    # If path starts with /library, it's a direct resource
    # But usually we want to use the transcode endpoint for resizing

    # Simple proxy for now: direct fetch
    # If the frontend requests /image/library/metadata/..., we fetch PLEX_URL/library/metadata/...

    url = f"{base_url}/{path}"

    # Forward query params
    params = {"X-Plex-Token": token}
    if width:
        params["width"] = str(width)
    if height:
        params["height"] = str(height)
    if min_size:
        params["minSize"] = str(min_size)

    # If usage is /image/transcode?url=... we need to point to /photo/:/transcode
    # specific handling for 'transcode' path component?
    # Let's assume the frontend sends the *Plex path* as the path param here.
    # But wait, next.config.js rewrites /image/:path* -> backend/image/:path*
    # So if frontend requests /image/library/metadata/1/thumb/123, backend gets path="library/metadata/1/thumb/123"

    client = httpx.AsyncClient(follow_redirects=True)
    try:
        req = client.build_request("GET", url, params=params)
        r = await client.send(req, stream=True)

        return StreamingResponse(
            r.aiter_bytes(),
            status_code=r.status_code,
            media_type=r.headers.get("content-type"),
            background=BackgroundTask(client.aclose),
        )
    except Exception:
        await client.aclose()
        logger.exception("Image proxy error")
        return Response(status_code=500, content="Image proxy failed")
