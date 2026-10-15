; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
; Fleet AI-client registration: McpClientsRegister/Unregister from the
; vendored mcp-clients.nsh (canonical: mcp-central-docs/scripts/nsis/).
; NOTE: the optional checkbox page (NSIS_HOOK_PAGES) needs the patched Tauri
; NSIS template, which this repo's build does not apply yet — registration
; therefore runs silently (the documented silent-install default).
!define MCP_REG_NAME "plex-mcp"
!define MCP_REG_EXE "plex-mcp-backend.exe"
!include "mcp-clients.nsh"
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

!macro NSIS_HOOK_POSTINSTALL
  !insertmacro McpClientsRegister
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillPlexFleetProcesses
  !insertmacro McpClientsUnregister
!macroend
