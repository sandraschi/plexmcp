# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with Plex MCP.

## Common Issues

### 1. Connection to Plex Server Fails

**Symptoms**:
- "Unable to connect to Plex server" errors
- Timeout when connecting to Plex

**Solutions**:
1. Verify Plex server is running and accessible
2. Check the PLEX_URL in your configuration
3. Ensure the PLEX_TOKEN is valid and has proper permissions
4. Check firewall settings to allow connections to the Plex server port (default: 32400)
5. Try accessing the Plex Web UI from the same machine

### 2. Authentication Failures

**Symptoms**:
- 401 Unauthorized errors
- "Invalid token" messages

**Solutions**:
1. Regenerate your Plex authentication token
2. Ensure the token has the correct permissions (all libraries, all devices)
3. Check for special characters in the token that might need URL encoding
4. Verify the token hasn't expired

### 3. Playback Issues

**Symptoms**:
- Media won't play on clients
- Playback starts but immediately stops

**Solutions**:
1. Verify the client device is turned on and connected to the network
2. Check if the media is accessible and not corrupted
3. Ensure the client has proper codecs installed
4. Check Plex server logs for transcoding issues

## Debugging

### Enable Debug Logging

Set the log level to DEBUG in your `.env` file:

```ini
LOG_LEVEL=DEBUG
```

### Check Logs

Logs are printed to stdout by default. You can redirect them to a file:

```powershell
# Windows
plexmcp run > plexmcp.log 2>&1

# Or with PowerShell
Start-Process -NoNewWindow -FilePath "plexmcp" -ArgumentList "run" -RedirectStandardOutput "plexmcp.log" -RedirectStandardError "plexmcp_error.log"
```

### Common Error Messages

| Error Message | Possible Cause | Solution |
|--------------|----------------|-----------|
| "Connection refused" | Plex server not running | Start Plex Media Server |
| 401 Unauthorized | Invalid or expired token | Regenerate PLEX_TOKEN |
| 404 Not Found | Invalid endpoint or media ID | Check API documentation |
| 500 Internal Server Error | Server-side issue | Check server logs |

## Performance Issues

### Slow Responses

1. Check network latency between Plex MCP and Plex Server
2. Monitor server resource usage (CPU, memory, disk I/O)
3. Optimize your Plex database
4. Consider increasing the server's resources

### High CPU Usage

1. Check for multiple instances of Plex MCP running
2. Look for infinite loops in custom scripts
3. Monitor for too many concurrent requests
4. Consider rate limiting clients

## Getting Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/yourusername/plexmcp/issues) for known issues
2. Enable debug logging and include the relevant portions when reporting issues
3. Provide the following information when seeking help:
   - Plex Server version
   - Plex MCP version
   - Operating System
   - Python version
   - Relevant error messages and logs

## Known Limitations

- Some Plex features may not be fully supported
- Performance may vary based on server hardware and network conditions
- Some operations may require Plex Pass subscription
