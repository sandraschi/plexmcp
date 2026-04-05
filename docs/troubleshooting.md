# Troubleshooting

## Common Startup Issues

### Server hangs during startup

**Symptoms:** Server starts but doesn't respond to input, appears to hang.

**Causes & Solutions:**

1. **Missing .env file or PLEX_TOKEN**
   ```powershell
   # Check if .env exists and has token
   Get-Content .env
   # Should contain: PLEX_TOKEN=your-token-here
   ```

2. **Plex server not accessible**
   ```powershell
   # Test Plex connection
   curl http://localhost:32400/identity
   # Should return XML with server info
   ```

3. **LLM sampling timeout** (if using server-side LLM)
   ```env
   # Fix: Use client-side sampling instead
   PLEX_SAMPLING_USE_CLIENT_LLM=1
   ```

### FastMCP 3.2 Compatibility Issues

**Symptoms:** Import errors, deprecated method warnings

**Solutions:**
- Ensure you're running PlexMCP v3.2.0+ with FastMCP 3.2.0+
- Update your virtual environment: `pip install -e .`
- Use new transport methods: `mcp.run()` instead of `mcp.run_stdio_async()`

### Environment Variable Issues

**Check current environment:**
```powershell
# Verify critical variables
$env:PLEX_TOKEN
$env:PLEX_BASE_URL
$env:PLEXMCP_ALLOW_LOGGING
$env:PLEX_SAMPLING_USE_CLIENT_LLM
```

**Fix missing variables:**
```powershell
# Create/update .env file
@"
PLEX_BASE_URL=http://localhost:32400
PLEX_TOKEN=your-x-plex-token
PLEXMCP_ALLOW_LOGGING=1
PLEX_SAMPLING_USE_CLIENT_LLM=1
"@ | Out-File -FilePath .env -Encoding utf8
```

## Plex authentication

- Regenerate the token from Plex Web (**Settings → Account → Authorized devices**) if requests return 401.  
- Test in a browser: `http://YOUR_PLEX:32400/?X-Plex-Token=YOUR_TOKEN`

## Connection refused

- Confirm Plex Media Server is running and the URL/port are correct (default **32400**).  
- Check firewalls and VPN/Tailscale if Plex is not on localhost.

## Empty libraries or search

- Confirm libraries exist in Plex and scans have completed.  
- Verify the token has access to that server.

## RAG / semantic search unavailable

- Ensure `docs_mcp.backend.rag_core` is importable ([RAG.md](RAG.md)).  
- Run **`sync_metadata`** once before **`semantic_search`**.

## *arr status unreachable

- Use the same base URL the browser uses to open Radarr/Sonarr/Lidarr.  
- From Docker, the backend must reach the container (host port, LAN IP, or reverse proxy).  
- API keys: each app → **Settings → General → Security**.

## Debug Mode

Enable detailed logging:
```powershell
$env:PLEXMCP_ALLOW_LOGGING = "1"
.venv\Scripts\python.exe -m plex_mcp.server --stdio --debug
```

## Test Suite

Run comprehensive tests to diagnose issues:
```powershell
.venv\Scripts\python.exe tests\test_server_startup.py
```

Expected output:
```
=== Test Results ===
Server Startup: PASS
MCP Protocol: PASS
Summary: 2/2 tests passed
🎉 All tests passed! PlexMCP is ready.
```

## Logging

Webapp backend logs: `logs/webapp.log` (rotating). Set `PLEXMCP_ALLOW_LOGGING` as documented in tests if FastMCP logging conflicts with your terminal.

## Getting Help

1. Run the test suite first to identify the issue
2. Check this troubleshooting guide
3. Enable debug logging for detailed error messages
4. Check GitHub Issues for known problems
5. Create a new issue with:
   - Test suite output
   - Debug logs
   - Environment variables (redacted)
