# Per-repo fleet start config for plex-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'plex-mcp'
    BackendPort  = 10740
    FrontendPort = 10741
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\plex-mcp\webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'app.main:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10740' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
