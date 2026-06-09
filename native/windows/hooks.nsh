; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillPlexFleetProcesses
  DetailPrint "Stopping Plex MCP processes..."
  ExecWait 'taskkill /F /IM plex-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM plex-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "plex-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "plex-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "plex-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "plex-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillPlexFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillPlexFleetProcesses
!macroend
