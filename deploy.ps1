# PlexMCP Deployment Script
# Automated setup and deployment for PlexMCP

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("stdio", "http", "webapp")]
    [string]$Mode = "stdio",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 10740,
    
    [Parameter(Mandatory=$false)]
    [string]$PlexToken,
    
    [Parameter(Mandatory=$false)]
    [string]$PlexUrl = "http://localhost:32400",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Checking prerequisites..." "Blue"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.1[2-9]") {
            Write-ColorOutput "✅ Python 3.12+ found: $pythonVersion" "Green"
        } else {
            Write-ColorOutput "❌ Python 3.12+ required. Found: $pythonVersion" "Red"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Python not found in PATH" "Red"
        return $false
    }
    
    # Check Plex server
    try {
        $response = Invoke-WebRequest -Uri "$PlexUrl/identity" -TimeoutSec 5 -ErrorAction Stop
        Write-ColorOutput "✅ Plex server accessible at $PlexUrl" "Green"
    } catch {
        Write-ColorOutput "❌ Plex server not accessible at $PlexUrl" "Red"
        Write-ColorOutput "   Ensure Plex Media Server is running" "Yellow"
        return $false
    }
    
    return $true
}

function Initialize-Environment {
    Write-ColorOutput "🔧 Setting up environment..." "Blue"
    
    # Create virtual environment if needed
    if (-not (Test-Path ".venv")) {
        Write-ColorOutput "Creating virtual environment..." "Yellow"
        python -m venv .venv
    } else {
        Write-ColorOutput "✅ Virtual environment exists" "Green"
    }
    
    # Activate virtual environment
    Write-ColorOutput "Activating virtual environment..." "Yellow"
    & .\.venv\Scripts\Activate.ps1
    
    # Install dependencies
    Write-ColorOutput "Installing dependencies..." "Yellow"
    pip install -e . --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to install dependencies" "Red"
        return $false
    }
    Write-ColorOutput "✅ Dependencies installed" "Green"
    
    # Setup .env file
    $envFile = ".env"
    $needsToken = $false
    
    if (-not (Test-Path $envFile) -or $Force) {
        Write-ColorOutput "Creating .env file..." "Yellow"
        
        if (-not $PlexToken) {
            Write-ColorOutput "❌ PLEX_TOKEN required. Use -PlexToken parameter" "Red"
            Write-ColorOutput "   Get your token from: Settings → Account → Authorized devices" "Yellow"
            return $false
        }
        
        $envContent = @"
# PlexMCP Configuration
PLEX_BASE_URL=$PlexUrl
PLEX_TOKEN=$PlexToken

# FastMCP Settings
PLEXMCP_ALLOW_LOGGING=1
PLEX_SAMPLING_USE_CLIENT_LLM=1

# Optional: Server-side LLM (uncomment to use)
# PLEX_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
# PLEX_SAMPLING_MODEL=llama3.2
"@
        
        $envContent | Out-File -FilePath $envFile -Encoding utf8
        Write-ColorOutput "✅ .env file created" "Green"
    } else {
        Write-ColorOutput "✅ .env file exists" "Green"
    }
    
    return $true
}

function Run-Tests {
    if ($SkipTests) {
        Write-ColorOutput "⏭️  Skipping tests (as requested)" "Yellow"
        return $true
    }
    
    Write-ColorOutput "🧪 Running test suite..." "Blue"
    
    try {
        $testOutput = python tests\test_server_startup.py 2>&1
        if ($testOutput -match "🎉 All tests passed") {
            Write-ColorOutput "✅ All tests passed" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ Tests failed" "Red"
            Write-ColorOutput $testOutput "Red"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Failed to run tests" "Red"
        Write-ColorOutput $_.Exception.Message "Red"
        return $false
    }
}

function Start-Server {
    Write-ColorOutput "🚀 Starting PlexMCP server..." "Blue"
    
    switch ($Mode) {
        "stdio" {
            Write-ColorOutput "Starting in STDIO mode (for Claude Desktop/MCP clients)..." "Cyan"
            Write-ColorOutput "Press Ctrl+C to stop" "Yellow"
            python -m plex_mcp.server --stdio
        }
        "http" {
            Write-ColorOutput "Starting in HTTP mode on port $Port..." "Cyan"
            Write-ColorOutput "Access MCP at: http://localhost:$Port/mcp" "Green"
            Write-ColorOutput "Press Ctrl+C to stop" "Yellow"
            python -m plex_mcp.server --http --port $Port
        }
        "webapp" {
            Write-ColorOutput "Starting full webapp..." "Cyan"
            Write-ColorOutput "Frontend: http://localhost:10741" "Green"
            Write-ColorOutput "Backend:  http://localhost:10740" "Green"
            Write-ColorOutput "Press Ctrl+C to stop" "Yellow"
            .\start.ps1
        }
    }
}

# Main execution
Write-ColorOutput "🎬 PlexMCP Deployment Script" "Cyan"
Write-ColorOutput "Mode: $Mode" "Blue"
Write-ColorOutput "Plex URL: $PlexUrl" "Blue"

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-ColorOutput "❌ Prerequisites failed. Exiting." "Red"
    exit 1
}

# Initialize environment
if (-not (Initialize-Environment)) {
    Write-ColorOutput "❌ Environment setup failed. Exiting." "Red"
    exit 1
}

# Run tests
if (-not (Run-Tests)) {
    if (-not $Force) {
        Write-ColorOutput "❌ Tests failed. Use -Force to override." "Red"
        exit 1
    } else {
        Write-ColorOutput "⚠️  Tests failed but proceeding (force mode)" "Yellow"
    }
}

# Start server
Write-ColorOutput "✅ Deployment complete!" "Green"
Start-Server
