# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

datas = [
    ("src/plex_mcp", "plex_mcp"),
    ("webapp/backend/app", "app"),
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
hiddenimports = []
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
    "_strptime",
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
    noarchive=False,
    optimize=0,
)
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
