# Restart Claude Desktop and Check MCP Server Loading
# This script restarts Claude Desktop and verifies PlexMCP loads correctly

param(
    [switch]$NoRestart,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 PlexMCP - Claude Desktop MCP Verification Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ClaudeProcessName = "Claude"
$ClaudeExe = "$env:LOCALAPPDATA\Programs\Claude\Claude.exe"
$LogPath = "$env:APPDATA\Claude\logs"
$MCPConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$WaitTime = 10

# Function: Check if Claude is running
function Test-ClaudeRunning {
    $process = Get-Process -Name $ClaudeProcessName -ErrorAction SilentlyContinue
    return $null -ne $process
}

# Function: Stop Claude Desktop
function Stop-Claude {
    Write-Host "🛑 Stopping Claude Desktop..." -ForegroundColor Yellow
    
    $process = Get-Process -Name $ClaudeProcessName -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        $process | Stop-Process -Force
        Start-Sleep -Seconds 2
        
        # Verify it stopped
        if (Test-ClaudeRunning) {
            Write-Host "❌ Failed to stop Claude Desktop" -ForegroundColor Red
            return $false
        }
        Write-Host "✅ Claude Desktop stopped" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Claude Desktop was not running" -ForegroundColor Gray
    }
    
    return $true
}

# Function: Start Claude Desktop
function Start-Claude {
    Write-Host "▶️  Starting Claude Desktop..." -ForegroundColor Yellow
    
    if (-not (Test-Path $ClaudeExe)) {
        Write-Host "❌ Claude Desktop executable not found at: $ClaudeExe" -ForegroundColor Red
        return $false
    }
    
    Start-Process $ClaudeExe
    Start-Sleep -Seconds $WaitTime
    
    # Verify it started
    if (Test-ClaudeRunning) {
        Write-Host "✅ Claude Desktop started" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Failed to start Claude Desktop" -ForegroundColor Red
        return $false
    }
}

# Function: Check MCP Configuration
function Test-MCPConfiguration {
    Write-Host ""
    Write-Host "🔍 Checking MCP Configuration..." -ForegroundColor Yellow
    
    if (-not (Test-Path $MCPConfigPath)) {
        Write-Host "❌ MCP config file not found: $MCPConfigPath" -ForegroundColor Red
        return $false
    }
    
    try {
        $config = Get-Content $MCPConfigPath -Raw | ConvertFrom-Json
        
        # Check for plexmcp server
        if ($config.mcpServers.PSObject.Properties.Name -contains "plex-mcp") {
            Write-Host "✅ PlexMCP server found in configuration" -ForegroundColor Green
            
            $plexConfig = $config.mcpServers.'plex-mcp'
            Write-Host "   Command: $($plexConfig.command)" -ForegroundColor Gray
            Write-Host "   Args: $($plexConfig.args -join ' ')" -ForegroundColor Gray
            
            # Check environment variables
            if ($plexConfig.env) {
                Write-Host "   Environment variables configured: $($plexConfig.env.PSObject.Properties.Name.Count)" -ForegroundColor Gray
            }
            
            return $true
        } else {
            Write-Host "❌ PlexMCP server not found in configuration" -ForegroundColor Red
            Write-Host "   Add PlexMCP to: $MCPConfigPath" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Error reading MCP config: $_" -ForegroundColor Red
        return $false
    }
}

# Function: Check recent logs for errors
function Test-MCPLogs {
    Write-Host ""
    Write-Host "📋 Checking Claude Desktop logs..." -ForegroundColor Yellow
    
    if (-not (Test-Path $LogPath)) {
        Write-Host "⚠️  Log directory not found: $LogPath" -ForegroundColor Yellow
        return $true  # Not critical
    }
    
    # Get most recent log file
    $latestLog = Get-ChildItem -Path $LogPath -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($null -eq $latestLog) {
        Write-Host "⚠️  No log files found" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "   Latest log: $($latestLog.Name)" -ForegroundColor Gray
    
    # Check for PlexMCP-related errors in last 50 lines
    $recentLines = Get-Content $latestLog.FullName -Tail 50
    $plexLines = $recentLines | Where-Object { $_ -match "plex" -or $_ -match "PlexMCP" }
    
    if ($plexLines) {
        Write-Host ""
        Write-Host "   Recent PlexMCP log entries:" -ForegroundColor Cyan
        $plexLines | ForEach-Object {
            if ($_ -match "error|fail|exception") {
                Write-Host "   ⚠️  $_" -ForegroundColor Red
            } elseif ($_ -match "warn") {
                Write-Host "   ⚠️  $_" -ForegroundColor Yellow
            } else {
                Write-Host "   ℹ️  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   No PlexMCP-specific entries found in recent logs" -ForegroundColor Gray
    }
    
    return $true
}

# Function: Test PlexMCP server directly
function Test-PlexMCPServer {
    Write-Host ""
    Write-Host "🧪 Testing PlexMCP server directly..." -ForegroundColor Yellow
    
    # Try to import and check basic structure
    $pythonCmd = "python"
    $testScript = @"
import sys
try:
    from plex_mcp import __version__
    print(f"✅ PlexMCP version {__version__} imported successfully")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error importing PlexMCP: {e}")
    sys.exit(1)
"@
    
    try {
        $result = $testScript | & $pythonCmd -c - 2>&1
        Write-Host "   $result" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })
        return $LASTEXITCODE -eq 0
    } catch {
        Write-Host "   ❌ Error running Python test: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "Starting MCP verification process..." -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Step 1: Restart Claude Desktop (unless -NoRestart specified)
if (-not $NoRestart) {
    if (Test-ClaudeRunning) {
        if (-not (Stop-Claude)) {
            $allPassed = $false
        }
    }
    
    if ($allPassed) {
        if (-not (Start-Claude)) {
            $allPassed = $false
        }
    }
} else {
    Write-Host "ℹ️  Skipping Claude Desktop restart (-NoRestart specified)" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Check MCP Configuration
if (-not (Test-MCPConfiguration)) {
    $allPassed = $false
}

# Step 3: Check logs
if (-not (Test-MCPLogs)) {
    $allPassed = $false
}

# Step 4: Test PlexMCP server directly
if (-not (Test-PlexMCPServer)) {
    $allPassed = $false
}

# Summary
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "✅ All checks passed! PlexMCP should be working correctly." -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Some checks failed. Review the output above for details." -ForegroundColor Yellow
    exit 1
}

