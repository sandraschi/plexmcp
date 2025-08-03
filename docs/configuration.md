# Configuration Guide

This document explains how to configure Plex MCP to work with your Plex Media Server.

## Environment Variables

Plex MCP can be configured using environment variables or a `.env` file in the project root.

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `PLEX_URL` | Base URL of your Plex server | `http://localhost:32400` |
| `PLEX_TOKEN` | Plex authentication token | `your_plex_token_here` |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `HOST` | `0.0.0.0` | Host to bind the server to |
| `PORT` | `8000` | Port to run the server on |
| `DEBUG` | `False` | Enable debug mode |
| `CORS_ORIGINS` | `["*"]` | List of allowed CORS origins |

## Configuration File

You can also use a `config.yaml` file in the project root:

```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8000
  debug: false

plex:
  url: http://localhost:32400
  token: your_plex_token_here

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Authentication

To get your Plex authentication token:

1. Sign in to [Plex Web](https://app.plex.tv)
2. Open Developer Tools (F12)
3. Go to the Application tab
4. Under Storage > Local Storage, find the `authToken` value

## Security Considerations

- Never commit your `PLEX_TOKEN` to version control
- Use environment variables for sensitive information
- Restrict CORS origins in production
- Run the server behind a reverse proxy with HTTPS in production

## Example Configuration for Production

```bash
# .env.production
PLEX_URL=https://your-plex-server.com
PLEX_TOKEN=your_production_token
LOG_LEVEL=WARNING
HOST=127.0.0.1
PORT=8000
```

## Testing Your Configuration

To verify your configuration:

```powershell
# Check environment variables
echo $env:PLEX_URL

# Test Plex connection
python -c "from plexapi.server import PlexServer; PlexServer('$env:PLEX_URL', '$env:PLEX_TOKEN').library.sections()"
```
