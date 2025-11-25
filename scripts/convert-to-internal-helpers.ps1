# Convert Old MCP Tools to Internal Helpers
# Removes @mcp.tool() decorators while preserving function logic

$filesToConvert = @(
    "src\plex_mcp\tools\media.py",
    "src\plex_mcp\tools\library.py",
    "src\plex_mcp\tools\sessions.py",
    "src\plex_mcp\tools\users.py",
    "src\plex_mcp\tools\playlists.py",
    "src\plex_mcp\tools\organization.py",
    "src\plex_mcp\tools\quality.py",
    "src\plex_mcp\tools\server.py",
    "src\plex_mcp\api\core.py",
    "src\plex_mcp\api\playback.py",
    "src\plex_mcp\api\playlists.py",
    "src\plex_mcp\api\admin.py",
    "src\plex_mcp\api\vienna.py"
)

Write-Host "Converting MCP tools to internal helpers..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $filesToConvert) {
    if (Test-Path $file) {
        Write-Host "Processing: $file" -ForegroundColor Cyan
        
        # Read content
        $content = Get-Content $file -Raw
        
        # Count decorators before
        $beforeCount = ([regex]::Matches($content, "@mcp\.tool\(\)")).Count
        
        # Remove @mcp.tool() decorators (with optional whitespace)
        $content = $content -replace "(?m)^\s*@mcp\.tool\(\)\s*\r?\n", ""
        
        # Also try removing @mcp_tool variants
        $content = $content -replace "(?m)^\s*@mcp_tool\s*\r?\n", ""
        
        # Count decorators after
        $afterCount = ([regex]::Matches($content, "@mcp\.tool\(\)")).Count
        
        # Write back
        Set-Content -Path $file -Value $content -NoNewline
        
        $removed = $beforeCount - $afterCount
        if ($removed -gt 0) {
            Write-Host "  ✅ Removed $removed @mcp.tool decorator(s)" -ForegroundColor Green
        } else {
            Write-Host "  ℹ️  No @mcp.tool decorators found" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Conversion complete!" -ForegroundColor Green
Write-Host "Old tools are now internal helper functions (not MCP-registered)" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test server starts: python -m plex_mcp.server" -ForegroundColor White
Write-Host "2. Verify only portmanteau tools are visible" -ForegroundColor White
Write-Host "3. Update portmanteau tools to call these internal functions" -ForegroundColor White


