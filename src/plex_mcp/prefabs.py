"""
Prefab card builders for PlexMCP — FastMCP 3.2 interactive visual cards.

Each builder takes structured data and returns a ``PrefabApp`` suitable for
``structured_content`` on a ``ToolResult``.

## Return Format
PrefabApp with interactive card-based UI components.

## Examples
build_library_grid([{"title": "Movies", "type": "movie", "count": 120}])
"""

from __future__ import annotations

from typing import Any

from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    H2,
    H3,
    H4,
    Badge,
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    DataTable,
    DataTableColumn,
    Grid,
    Metric,
    P,
    Row,
    Separator,
    Small,
)


def _value(v: Any, default: str = "") -> str:
    return str(v) if v is not None else default


def build_library_grid(libraries: list[dict[str, Any]]) -> PrefabApp:
    """Grid of library section cards for the ``plex_library_grid`` prefab."""
    with PrefabApp(title="Plex Libraries") as app:
        H2("Media Libraries")
        P("All configured Plex library sections.")
        Separator(spacing=4)
        with Grid(columns={"default": 1, "md": 2, "lg": 3}, gap=4):
            for lib in libraries:
                lib_type = _value(lib.get("type"))
                lib_count = _value(lib.get("count", lib.get("total", 0)))
                with Card():
                    with CardHeader():
                        CardTitle(_value(lib.get("title", lib.get("name", "Library"))))
                        CardDescription(f"Type: {lib_type}")
                    with CardContent():
                        Metric(label="Items", value=lib_count)
    return app


def build_library_detail(library: dict[str, Any]) -> PrefabApp:
    """Detail card for a single library section."""
    title = _value(library.get("title", library.get("name", "Library")))
    lib_type = _value(library.get("type"))
    lib_count = _value(library.get("count", library.get("total", 0)))
    locations = library.get("locations", [])
    agent = _value(library.get("agent"))
    scanner = _value(library.get("scanner"))
    language = _value(library.get("language"))

    with PrefabApp(title=title) as app:
        with Row():
            H2(title)
            Badge(lib_type, variant="info")
        Separator(spacing=4)
        with Grid(columns={"default": 1, "md": 2, "lg": 3}, gap=4):
            Metric(label="Items", value=lib_count)
            Metric(label="Agent", value=agent or "default")
            Metric(label="Scanner", value=scanner or "default")
            if language:
                Metric(label="Language", value=language)
        if locations:
            H4("Media Locations")
            for loc in locations:
                P(_value(loc))
    return app


def build_media_browser(items: list[dict[str, Any]], title: str = "Media Browser") -> PrefabApp:
    """Grid of media items for the ``plex_media_browser`` prefab."""
    with PrefabApp(title=title) as app:
        H2(title)
        P(f"{len(items)} items")
        Separator(spacing=4)
        with Grid(columns={"default": 1, "md": 2, "lg": 3, "xl": 4}, gap=4):
            for item in items:
                item_title = _value(item.get("title", item.get("name", "Unknown")))
                item_year = _value(item.get("year"))
                item_type = _value(item.get("type"))
                item_rating = _value(item.get("rating"))
                with Card():
                    with CardHeader():
                        CardTitle(item_title)
                        CardDescription(f"{item_type}{' - ' + str(item_year) if item_year else ''}")
                    with CardContent():
                        if item_rating:
                            Metric(label="Rating", value=item_rating)
    return app


def build_media_detail(item: dict[str, Any]) -> PrefabApp:
    """Detail card for a single media item."""
    title = _value(item.get("title", "Unknown"))
    year = item.get("year")
    summary = _value(item.get("summary", item.get("plot", "")))
    rating = item.get("rating")
    content_rating = _value(item.get("content_rating"))
    duration = item.get("duration")
    genres = item.get("genres", [])
    studio = _value(item.get("studio"))
    tagline = _value(item.get("tagline"))
    actors = item.get("actors", [])
    directors = item.get("directors", [])

    with PrefabApp(title=title) as app:
        H2(f"{title}{' (' + str(year) + ')' if year else ''}")
        if tagline:
            P(tagline)
        Separator(spacing=2)
        info_parts = []
        if rating:
            info_parts.append(f"Rating: {rating}")
        if content_rating:
            info_parts.append(content_rating)
        if duration:
            mins = int(duration) / 60000 if duration > 100000 else int(duration)
            info_parts.append(f"{int(mins)} min")
        if info_parts:
            P(" | ".join(info_parts))
        Separator(spacing=4)
        with Grid(columns={"default": 1, "md": 2}, gap=4):
            if summary:
                with Card():
                    with CardHeader():
                        CardTitle("Summary")
                    with CardContent():
                        P(summary)
            if genres:
                with Card():
                    with CardHeader():
                        CardTitle("Genres")
                    with CardContent():
                        with Row():
                            for g in genres:
                                Badge(g, variant="secondary")
            if directors:
                with Card():
                    with CardHeader():
                        CardTitle("Director")
                    with CardContent():
                        P(", ".join(directors))
            if studio:
                with Card():
                    with CardHeader():
                        CardTitle("Studio")
                    with CardContent():
                        P(studio)
        if actors:
            Separator(spacing=4)
            H3("Cast")
            with Grid(columns={"default": 2, "md": 3, "lg": 4}, gap=2):
                for actor in actors:
                    name = _value(actor.get("name", actor.get("tag", "")))
                    role = actor.get("role")
                    Small(f"{name}{' as ' + role if role else ''}")
    return app


def build_server_status(status: dict[str, Any]) -> PrefabApp:
    """Dashboard card for Plex server status."""
    version = _value(status.get("version"))
    uptime = _value(status.get("uptime"))
    sessions = status.get("sessions", status.get("active_sessions", 0))
    library_value = status.get("libraries", status.get("library_count", 0))
    libraries = len(library_value) if isinstance(library_value, (list, tuple, set, dict)) else library_value
    is_reachable = status.get("reachable", status.get("online", status.get("connected", False)))

    with PrefabApp(title="Plex Server Status") as app:
        with Row():
            H2("Server Status")
            Badge("Online" if is_reachable else "Offline", variant="success" if is_reachable else "destructive")
        Separator(spacing=4)
        with Grid(columns={"default": 2, "md": 4}, gap=4):
            Metric(label="Version", value=version)
            Metric(label="Uptime", value=uptime)
            Metric(label="Active Sessions", value=str(sessions))
            Metric(label="Libraries", value=str(libraries))
    return app


def build_server_info(info: dict[str, Any]) -> PrefabApp:
    """Info card for Plex server details."""
    name = _value(info.get("name", info.get("friendlyName", "Plex Server")))
    platform = _value(info.get("platform"))
    version = _value(info.get("version"))
    machine_id = _value(info.get("machineIdentifier", ""))
    multiuser = info.get("multiuser", False)

    with PrefabApp(title=name) as app:
        H2(name)
        Badge("Multi-user" if multiuser else "Single user", variant="info")
        Separator(spacing=4)
        with Grid(columns={"default": 1, "md": 2, "lg": 3}, gap=4):
            Metric(label="Platform", value=platform)
            Metric(label="Version", value=version)
            if machine_id:
                Metric(label="Machine ID", value=machine_id[:8] + "...")
    return app


def build_performance_dashboard(stats: dict[str, Any]) -> PrefabApp:
    """Dashboard for Plex performance metrics."""
    streams = stats.get("streams", stats.get("active_sessions", 0))
    bandwidth = _value(stats.get("bandwidth", stats.get("total_bandwidth", "0")))
    transcodes = stats.get("transcodes", stats.get("active_transcodes", 0))
    direct_plays = stats.get("direct_plays", stats.get("directPlay", 0))
    cpu = stats.get("cpu", stats.get("cpu_usage", ""))
    memory = stats.get("memory", stats.get("memory_usage", ""))

    with PrefabApp(title="Performance Dashboard") as app:
        H2("Performance")
        Separator(spacing=4)
        with Grid(columns={"default": 2, "md": 3}, gap=4):
            Metric(label="Active Streams", value=str(streams))
            Metric(label="Transcodes", value=str(transcodes))
            Metric(label="Direct Play", value=str(direct_plays))
            if bandwidth:
                Metric(label="Bandwidth", value=str(bandwidth))
            if cpu:
                Metric(label="CPU", value=str(cpu))
            if memory:
                Metric(label="Memory", value=str(memory))
        Separator(spacing=4)
        P("Streams are distributed between direct play and transcoded sessions.")
    return app


def build_streaming_session(sessions: list[dict[str, Any]]) -> PrefabApp:
    """Card for active streaming sessions."""
    count = len(sessions)

    with PrefabApp(title=f"Streaming Sessions ({count})") as app:
        H2("Active Sessions")
        if count == 0:
            P("No active streaming sessions.")
        else:
            Badge(str(count), variant="success")
            Separator(spacing=4)
            DataTable(
                columns=[
                    DataTableColumn(key="user", header="User", sortable=True),
                    DataTableColumn(key="title", header="Media", sortable=True),
                    DataTableColumn(key="state", header="State"),
                    DataTableColumn(key="bitrate", header="Bitrate"),
                ],
                rows=[
                    {
                        "user": _value(s.get("user", {}).get("title", "Unknown")),
                        "title": _value(s.get("title", s.get("media", {}).get("title", ""))),
                        "state": _value(s.get("state", s.get("session", {}).get("state", "playing"))),
                        "bitrate": _value(s.get("bitrate", "")),
                    }
                    for s in sessions
                ],
                search=True,
                paginated=count > 20,
                page_size=min(count, 20) or 10,
            )
    return app


def build_streaming_client(clients: list[dict[str, Any]]) -> PrefabApp:
    """Card for connected Plex clients."""
    count = len(clients)

    with PrefabApp(title=f"Plex Clients ({count})") as app:
        H2("Connected Clients")
        if count == 0:
            P("No clients connected.")
        else:
            Separator(spacing=4)
            with Grid(columns={"default": 1, "md": 2, "lg": 3}, gap=4):
                for client in clients:
                    name = _value(client.get("name", client.get("title", "Unknown")))
                    device = _value(client.get("device", client.get("product", "")))
                    platform = _value(client.get("platform", ""))
                    state = _value(client.get("state", "idle"))
                    with Card():
                        with CardHeader():
                            CardTitle(name)
                            CardDescription(device or platform)
                        with CardContent():
                            Small(state)
    return app
