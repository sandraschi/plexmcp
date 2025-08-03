# API Reference

This document provides detailed information about the Plex MCP API endpoints.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

All API requests require authentication using a Bearer token.

```http
Authorization: Bearer your_plex_token_here
```

## Endpoints

### Media

- `GET /api/v1/media` - List all media items
- `GET /api/v1/media/{id}` - Get media item details
- `GET /api/v1/media/search?query={query}` - Search media

### Libraries

- `GET /api/v1/libraries` - List all libraries
- `GET /api/v1/libraries/{id}` - Get library details
- `GET /api/v1/libraries/{id}/items` - List items in a library

### Playback

- `POST /api/v1/playback/play` - Start playback
- `POST /api/v1/playback/pause` - Pause playback
- `POST /api/v1/playback/stop` - Stop playback
- `POST /api/v1/playback/next` - Play next item
- `POST /api/v1/playback/previous` - Play previous item

### Playlists

- `GET /api/v1/playlists` - List all playlists
- `POST /api/v1/playlists` - Create a new playlist
- `GET /api/v1/playlists/{id}` - Get playlist details
- `PUT /api/v1/playlists/{id}` - Update playlist
- `DELETE /api/v1/playlists/{id}` - Delete playlist

### System

- `GET /api/v1/system/info` - Get system information
- `GET /api/v1/system/health` - Check system health
- `GET /api/v1/system/version` - Get version information

## Response Format

All API responses follow the same JSON format:

```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-08-03T02:00:00Z"
}
```

## Error Handling

Errors follow this format:

```json
{
  "status": "error",
  "error": {
    "code": 404,
    "message": "Resource not found",
    "details": "The requested resource was not found"
  },
  "timestamp": "2025-08-03T02:00:00Z"
}
```

## Rate Limiting

- 100 requests per minute per IP address
- Exceeding the limit will result in a 429 status code

## Versioning

API versioning is done through the URL path (e.g., `/api/v1/...`).

## Pagination

Endpoints that return lists support pagination:

```http
GET /api/v1/media?page=1&per_page=20
```

Response includes pagination metadata:

```json
{
  "status": "success",
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 100,
    "total_pages": 5
  }
}
```
