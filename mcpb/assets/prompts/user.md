# PlexMCP User Instructions

Welcome to PlexMCP -- your all-in-one Plex Media Server assistant powered by FastMCP 3.4+. This guide covers everything you need to know to manage your Plex server efficiently.

## Getting Started

### Prerequisites
Before using PlexMCP, ensure you have:
- Plex Media Server running and accessible on your network
- A Plex authentication token from https://plex.tv/pms/servers
- Python 3.12 or higher
- FastMCP 3.4+ and the dependencies from pyproject.toml

### Configuration
Set these environment variables or provide them via the MCP client configuration:
- PLEX_URL: Your Plex server URL (default: http://localhost:32400)
- PLEX_TOKEN: Your Plex authentication token

### Quick Start Commands
1. "Check my server status" -- Runs plex_server(operation="status") to show server health, version, uptime, and active sessions.
2. "Show my libraries" -- Runs plex_library(operation="list") to enumerate all media libraries.
3. "What's recently added?" -- Runs plex_media(operation="get_recent") to list new content.
4. "Search for Inception" -- Runs plex_search(operation="global", query="Inception") to find media.
5. "Who's watching?" -- Runs plex_streaming(operation="sessions") to show active playback.

## How to Ask for Things

### Library Management
- "List all my libraries" -- Shows every library section with type, path, and item count.
- "Scan my Movies library" -- Triggers a library scan. Specify the library name or ID.
- "Create a new TV library at /media/tvshows" -- Creates a library; provide the type, name, and path.
- "Empty the trash in my library" -- Clears deleted media from library trash.
- "Optimize the 4K Movies library" -- Triggers library optimization.
- "Show library statistics for Movies" -- Gets per-library stats including total file size.
- "Add /media/newfolder to my TV library" -- Adds a new path to an existing library.
- "Remove the path /media/old from my Movies library" -- Removes a path from a library.
- "Configure my Movies library to use Plex Movie agent" -- Changes library configuration.

### Media Browsing and Discovery
- "Browse my Movies library" -- Fetches items from a library with pagination.
- "Show me recently added movies from the last week" -- Lists recently added media with a time filter.
- "What movies are recommended for me?" -- Shows personalized recommendations.
- "Find movies similar to Inception" -- Uses the similar endpoint to show related content.
- "Show me the stream info for this movie" -- Gets direct play and transcode URLs.
- "What resolution is this movie in?" -- Inspects media item details including streams.
- "Refresh metadata for this item" -- Forces a metadata refresh on a specific media item.
- "Delete this movie from my library" -- Removes a media item permanently.

### Searching
- "Find all Christopher Nolan movies" -- Global search with director context.
- "Search for action movies from 2020" -- Advanced search with year and genre filters.
- "Show me all movies starring Tom Hanks" -- People search by actor name.
- "What content is from Warner Bros?" -- Studio filter search.
- "Suggest movies starting with 'The Dark'" -- Typeahead suggestions.
- "Show my saved searches" -- Lists previously saved search filters.
- "Find all 4K movies in my library" -- Advanced search with resolution filter.
- "Search for TV shows with more than 5 seasons" -- Advanced search with episode count filter.

### Streaming and Sessions
- "What's currently playing?" -- Shows active playback sessions.
- "Who is watching and on what device?" -- Session details with user and device info.
- "Show me all transcoding sessions" -- Filters sessions by transcode activity.
- "What's the current bandwidth usage?" -- Bandwidth monitoring across all sessions.
- "Show me remote streams" -- Filters sessions by remote IP origin.
- "Stop the session on the living room TV" -- Kills a specific session.
- "How many direct play streams are active?" -- Direct play monitoring.
- "Show me LAN streams only" -- Filters by local network origin.

### Server Management
- "What version of Plex am I running?" -- Server version and update status.
- "Show me the server health dashboard" -- Comprehensive health check.
- "Show recent server logs" -- Fetches latest log entries for troubleshooting.
- "List scheduled server tasks" -- Shows all maintenance tasks.
- "Run the 'Optimize database' task" -- Triggers a specific maintenance task.
- "How full is my server disk?" -- Disk usage from the health endpoint.
- "Restart the Plex server" -- Triggers a server restart.
- "Check for server updates" -- Checks if a newer Plex version is available.

### User Management
- "Who has access to my server?" -- Lists all users with permissions.
- "Show me details for user John" -- Detailed user profile and restrictions.
- "Invite a new user with Movies only access" -- Creates a new managed user.
- "Set viewing restrictions for my kids' account" -- Configures content filters and time limits.
- "What has user Sarah been watching?" -- User activity and watch history.
- "How many devices does user Bob have?" -- Lists authorized devices for a user.
- "Update user Jane's permissions to include TV libraries" -- Modifies user access.
- "Change user password" -- Updates user account password.

### Playlists
- "List all my playlists" -- Shows all playlists with item counts.
- "Show the details of my 'Weekend Binge' playlist" -- Detailed playlist view.
- "Create a new playlist called 'Action Night'" -- Creates a new playlist.
- "Add Inception to my 'Sci-Fi Favorites' playlist" -- Adds items to an existing playlist.
- "Remove the movie Tenet from my playlist" -- Removes items from a playlist.
- "Share my 'Family Movie Night' playlist" -- Generates a share link.
- "Rename my 'Old' playlist to 'Classics'" -- Updates playlist metadata.
- "Delete the 'Temp' playlist" -- Removes a playlist entirely.

### Collections
- "List all collections in my Movies library" -- Enumerates collections with item counts.
- "Show me the 'MCU' collection" -- Gets detailed collection content.
- "Create a 'Christopher Nolan' collection" -- Creates a new collection with items.
- "Add Interstellar to my 'Space Movies' collection" -- Adds items to a collection.
- "Remove Tenet from my 'Nolan' collection" -- Removes items from a collection.
- "Delete the 'Test' collection" -- Removes a collection.
- "Update the '80s Classics' collection description" -- Changes collection metadata.

### Metadata Management
- "Show me the full metadata for Inception" -- Gets all metadata fields including external IDs.
- "Update the summary for The Dark Knight" -- Modifies metadata text fields.
- "Refresh metadata for season 1 of Breaking Bad" -- Triggers metadata refresh.
- "Manually match this movie with TMDB ID 155" -- Identifies a media item with an external ID.
- "Set the poster for Interstellar to a specific image" -- Manages artwork images.
- "Lock the title and year for this movie" -- Prevents automatic metadata overwrites.
- "Unlock the summary field" -- Re-enables automatic updates for a field.
- "Fetch fresh metadata from TVDB for Game of Thrones" -- Pulls from an external provider.

### Library Organization
- "Analyze my Movies library for issues" -- Scans for naming and metadata problems.
- "Find duplicate movies in my library" -- Identifies duplicate items.
- "Fix incorrect matching for The Matrix" -- Corrects misidentified media.
- "Add the tag 'favorites' to all Nolan movies" -- Bulk tags across multiple items.
- "Audit file naming in my TV library" -- Validates naming conventions.

### Performance Monitoring
- "How is my server performing?" -- Real-time health and performance metrics.
- "Show me system stats" -- CPU, memory, and bandwidth utilization.
- "What's the transcode capacity?" -- Transcode performance and queue status.
- "Show library-level performance" -- Per-library metrics.
- "Monitor bandwidth usage" -- Real-time bandwidth consumption.

### Quality Profiles
- "Show me available quality profiles" -- Lists transcode quality options.
- "Set transcoding to 1080p for remote streams" -- Configures quality settings.
- "Check for optimized versions of The Matrix" -- Lists available optimized versions.
- "Compare quality profiles" -- Side-by-side profile comparison.

### Reporting and Analytics
- "Show me library statistics" -- Aggregate counts and sizes.
- "What are the most-watched movies this month?" -- Popular content ranking.
- "Show me genre distribution" -- Genre breakdown across libraries.
- "What resolution is most of my content in?" -- Resolution distribution.
- "Show codec usage in my library" -- Audio and video codec analysis.
- "What has user Sarah watched this week?" -- Per-user activity report.
- "Export a report of all my 4K content" -- Structured report export in CSV.
- "Show recently watched items" -- Recent playback activity.

### Semantic Search with RAG
- "Find dark sci-fi movies from the 90s" -- Semantic search over metadata.
- "What documentaries about ocean life do I have?" -- Natural language query.
- "Sync the RAG index" -- Rebuild the vector database from scratch.
- "Check RAG indexing status" -- Shows how many items are indexed.
- "Purge and re-index the RAG database" -- Clears and rebuilds the index.
- "Find movies like The Shining but happy" -- Semantic similarity query.
- "Recommend something for a rainy Sunday" -- Contextual recommendation query.

### External Services Integration
- "Check *Arr service health" -- Verifies Radarr, Sonarr, Lidarr connectivity.
- "Show the Radarr download queue" -- Inspects *Arr download queues.
- "Export my Plex configuration" -- Creates a portable configuration backup.
- "Restore from backup" -- Restores a previous configuration snapshot.
- "Enrich Inception's metadata from TMDB" -- Fetches external metadata enrichments.
- "Get Wikipedia info for Breaking Bad" -- Wikipedia enrichment for media items.
- "Batch enrich all recently added movies" -- Bulk enrichment operation.

### Audio Management
- "Show audio system status" -- Audio subsystem health check.
- "List my music libraries" -- Music library enumeration with artist counts.
- "What audio codecs are available?" -- Codec capability inspection.
- "Check audio transcoding activity" -- Audio transcode monitoring.
- "Set audio quality to high" -- Audio quality configuration.
- "Optimize my music library" -- Music library optimization trigger.

### FFmpeg and Transcoding
- "Show available transcode profiles" -- Hardware acceleration profile listing.
- "Detect hardware acceleration" -- GPU detection for HW transcoding.
- "Benchmark transcode performance" -- Performance comparison across profiles.
- "Test the FFmpeg configuration" -- Transcode test and verification.
- "Set the FFmpeg path" -- FFmpeg binary path configuration.
- "Compare profile performance" -- Side-by-side benchmark results.

### Complex Workflow Examples

"I want to clean up my library":
1. plex_organization(operation="analyze", library_id="1") -- Scans for issues.
2. plex_library(operation="cleanup", library_id="1") -- Cleans orphaned metadata.
3. plex_organization(operation="deduplicate", library_id="1") -- Finds duplicates.
4. plex_organization(operation="fix_matching") -- Fixes incorrect matches.

"Set up a movie night":
1. plex_media(operation="get_recommended") -- Gets recommendations.
2. plex_search(operation="advanced", query="action", year=2024) -- Searches for recent action.
3. plex_playlist(operation="create", name="Movie Night", items=[...]) -- Builds a playlist.
4. plex_streaming(operation="sessions") -- Monitors who's watching.

"Diagnose streaming issues":
1. plex_performance(operation="get_server_status") -- Server health check.
2. plex_streaming(operation="transcode") -- Find transcode bottlenecks.
3. plex_server(operation="health") -- Full system diagnostics.
4. plex_server(operation="logs", lines=100) -- Recent error log inspection.

"Onboard a new user":
1. plex_user(operation="list") -- See current users.
2. plex_user(operation="create", name="NewUser", password="...") -- Create account.
3. plex_user(operation="update", user_id="...", policy={...}) -- Set restrictions.
4. plex_library(operation="list") -- Show available libraries for sharing.

"Organize by collection":
1. plex_search(operation="people", person="Christopher Nolan") -- Find Nolan films.
2. plex_collections(operation="create", name="Nolan Collection", library_id="1") -- Create collection.
3. plex_collections(operation="add_items", collection_id="...", item_ids=[...]) -- Add films.
4. plex_metadata(operation="update", rating_key="...", metadata={"tagline":"..."}) -- Polish metadata.

"Monthly server report":
1. plex_reporting(operation="stats") -- Aggregate statistics.
2. plex_reporting(operation="user_activity") -- Per-user watch time.
3. plex_reporting(operation="popular", limit=20) -- Top content.
4. plex_reporting(operation="export", format="csv") -- Exportable report.

"Find 4K HDR content":
1. plex_search(operation="advanced", types="Movie", filters="IsUnplayed") -- Unwatched movies.
2. plex_reporting(operation="resolution", library_id="1") -- Resolution breakdown.
3. plex_media(operation="search", query="4K") -- Search for 4K content.
4. plex_reporting(operation="export", format="csv") -- Export findings.

"Sync with *Arr services":
1. arr_stack(operation="health") -- Check all service connections.
2. arr_stack(operation="queue", service="radarr") -- Radarr download queue.
3. arr_stack(operation="history", service="sonarr") -- Sonarr import history.
4. plex_library(operation="scan") -- Scan after *Arr imports.

## Troubleshooting Tips

Server unreachable: Check PLEX_URL is correct and the server is running. Use plex_server(operation="status") to diagnose.

Empty search results: Try plex_rag(operation="sync") to rebuild the search index, then retry the query.

Transcode errors: Use plex_ffmpeg_mgr(operation="detect_hw") to check GPU support, then plex_ffmpeg_mgr(operation="test") to verify FFmpeg.

User cannot see content: Check user policy with plex_user(operation="policy", user_id="...") and library sharing with plex_library(operation="list").

Slow server: Monitor with plex_performance(operation="get_server_status") and check active sessions via plex_streaming(operation="sessions").

Playback buffering: Check transcode health with plex_streaming(operation="transcode") and network with plex_server(operation="health").

Metadata not updating: Use plex_metadata(operation="refresh", rating_key="...") to force refresh, or plex_metadata(operation="identify", ...) for manual matching.

Collection not visible: Collections are library-scoped. Use plex_collections(operation="list") to find all collections and their libraries.

Playlist missing items: Check playlist contents with plex_playlist(operation="get", playlist_id="...") and verify items exist in the library.

API token invalid: Regenerate your token at https://plex.tv/pms/servers and update PLEX_TOKEN.

## Best Practices

Always use plex_library(operation="list") first to get library IDs -- they are numbers required by many tools.

For bulk operations, always call plex_organization(operation="analyze") first to preview changes before modifying.

Use plex_reporting(operation="export") with format="csv" for offline analysis and record-keeping.

Keep the RAG index synced with plex_rag(operation="sync") after large library changes for best semantic search results.

Monitor streaming regularly with plex_streaming(operation="sessions") to catch performance issues early.

Create regular backups with plex_integration(operation="backup") to protect your configuration and metadata.

Use plex_collections for thematic grouping but plex_playlist for temporal or disposable groupings.

For metadata-heavy workflows, use plex_media_enrichment(operation="batch") after adding new content.

When troubleshooting, always start with plex_server(operation="health") for a full diagnostic overview.
