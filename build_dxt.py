#!/usr/bin/env python3
"""
Build script for Plex MCP DXT package
"""
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

def read_manifest() -> Dict[str, Any]:
    """Read and validate the DXT manifest file."""
    manifest_path = Path("dxt_manifest.json")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Basic validation
    required_fields = ["name", "version", "description", "prompts"]
    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Missing required field in manifest: {field}")
    
    return manifest

def create_package_dir() -> Path:
    """Create package directory structure."""
    dist_dir = Path("dist")
    pkg_dir = dist_dir / "plex-mcp"
    
    # Clean and create directories
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    
    pkg_dir.mkdir(parents=True, exist_ok=True)
    return pkg_dir

def copy_package_files(pkg_dir: Path) -> None:
    """Copy package files to the build directory."""
    # Copy Python package
    shutil.copytree("src/plex_mcp", pkg_dir / "plex_mcp")
    
    # Copy manifest
    shutil.copy2("dxt_manifest.json", pkg_dir)
    
    # Copy other required files
    for f in ["README.md", "pyproject.toml", "setup.py"]:
        if Path(f).exists():
            shutil.copy2(f, pkg_dir)
    
    # Create __init__.py if it doesn't exist
    init_file = pkg_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()

def build_dxt_package(pkg_dir: Path) -> None:
    """Build the DXT package."""
    # Create a zip archive of the package
    shutil.make_archive(
        str(pkg_dir.parent / "plex-mcp"),
        'zip',
        root_dir=pkg_dir.parent,
        base_dir=pkg_dir.name
    )
    
    # Rename to .dxt
    zip_path = pkg_dir.parent / "plex-mcp.zip"
    dxt_path = pkg_dir.parent / "plex-mcp.dxt"
    
    if dxt_path.exists():
        dxt_path.unlink()
    
    zip_path.rename(dxt_path)
    print(f"\n✅ DXT package built: {dxt_path}")

def main() -> None:
    """Main function to build the DXT package."""
    print("🚀 Building Plex MCP DXT package...")
    
    # Read and validate manifest
    print("📋 Validating manifest...")
    manifest = read_manifest()
    print(f"✅ Found {len(manifest['prompts'])} prompt templates")
    
    # Create package directory
    print("📁 Creating package structure...")
    pkg_dir = create_package_dir()
    
    # Copy files
    print("📂 Copying package files...")
    copy_package_files(pkg_dir)
    
    # Build package
    print("🔨 Building DXT package...")
    build_dxt_package(pkg_dir)
    
    print("\n✨ Package build complete!")
    print(f"📦 Package location: {pkg_dir.parent / 'plex-mcp.dxt'}")

if __name__ == "__main__":
    main()
