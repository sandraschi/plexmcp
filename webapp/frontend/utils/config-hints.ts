/** User-facing setup hints — installed Tauri app uses Settings, not .env files. */

export const IS_DESKTOP_BUILD = process.env.NODE_ENV !== "development";

export const PLEX_TOKEN_HINT = IS_DESKTOP_BUILD
	? "Open Settings → Plex, enter your server URL and Plex token (X-Plex-Token), then save."
	: "Open Settings, or set PLEX_TOKEN in webapp/backend/.env for dev.";

export const BACKEND_DOWN_HINT = IS_DESKTOP_BUILD
	? "Restart Plex MCP. If it persists, check %LOCALAPPDATA%\\ai.fleet.plex-mcp\\logs\\backend-spawn.log"
	: "Start the backend: cd webapp; powershell -ExecutionPolicy Bypass -File .\\start.ps1";

export const PLEX_AUTH_HINT =
	"Verify Plex URL (e.g. http://127.0.0.1:32400) and token in Settings → Plex.";
