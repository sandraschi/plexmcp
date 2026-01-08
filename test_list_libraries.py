#!/usr/bin/env python3
"""Test plex list libraries functionality."""

import sys
sys.path.insert(0, 'src')
import asyncio

async def test_list_libraries():
    try:
        from plex_mcp.config import get_settings
        from plex_mcp.services.plex_service import PlexService

        config = get_settings()
        service = PlexService(config.server_url, config.plex_token)

        print('Testing plex_library list operation...')
        libraries = await service.list_libraries()

        print(f'Found {len(libraries)} libraries:')
        for i, lib in enumerate(libraries, 1):
            title = lib.get('title', 'Unknown')
            lib_type = lib.get('type', 'unknown')
            lib_id = lib.get('id', 'unknown')
            count = lib.get('count', 0)

            print(f'  {i}. {title} ({lib_type})')
            print(f'     ID: {lib_id}')
            print(f'     Count: {count} items')
            print()

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_list_libraries())