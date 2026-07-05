# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

datas = [
    ("src/plex_mcp", "plex_mcp"),
    ("webapp/backend/app", "app"),
    ("webapp/frontend/out", "webapp/frontend/out"),
]
for pkg in (
    "fastmcp",
    "fastapi",
    "uvicorn",
    "pydantic",
    "starlette",
    "httpx",
    "prefab_ui",
    "pytz",
    "jsonschema",
):
    datas += copy_metadata(pkg)

binaries = []
hiddenimports = [
    "_strptime",
]
for pkg in ("cachetools", "beartype", "pytz", "jsonschema"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

hiddenimports += collect_submodules("plex_mcp")
hiddenimports += collect_submodules("app")
hiddenimports += collect_submodules("key_value")
hiddenimports += collect_submodules("cachetools")
hiddenimports += [
    # stdlib C extensions (lazy-imported; Movies browse hits datetime.strptime)

    "_datetime",
    "sqlite3",
    "_sqlite3",
    "netrc",
    # FastMCP / uvicorn chain (calibre parity)
    "fastmcp",
    "mcp",
    "fastapi",
    "starlette",
    "h11",
    "httptools",
    "beartype",
    "beartype.claw",
    "beartype.claw._ast",
    "beartype.claw._ast._clawaststar",
    "websockets",
    "websockets.legacy",
    "websockets.legacy.handshake",
    "cachetools",
    "cachetools.keys",
    "key_value",
    "key_value.aio",
    "key_value.aio.stores",
    "key_value.aio.stores.memory",
    "pytz",
    "jsonschema",
    "jwt",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "app.main",
    "plex_mcp.server",
]

a = Analysis(
    ["run_server.py"],
    pathex=["src", "webapp/backend"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "torchvision",
        "torchaudio",
        "tensorboard",
    ],
    noarchive=True,
    optimize=0,
)
# Strip .dist-info but preserve metadata for packages that need it at runtime
_keep_dist = ['fastmcp-', 'mcp-', 'prefab_ui-', 'opentelemetry-', 'email_validator-']
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
a.datas.extend(_saved)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    
    name="plex-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)





