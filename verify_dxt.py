#!/usr/bin/env python3
"""
Verification script for Plex MCP DXT package
"""
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any

def verify_dxt_package(dxt_path: Path) -> bool:
    """Verify the contents of a DXT package."""
    if not dxt_path.exists():
        print(f"❌ DXT package not found: {dxt_path}")
        return False
    
    # Extract to temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        try:
            # Extract the DXT package (which is a zip file)
            with zipfile.ZipFile(dxt_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir_path)
            
            # Check for required files
            required_files = [
                "dxt_manifest.json",
                "setup.py",
                "pyproject.toml",
                "plex_mcp/__init__.py",
                "plex_mcp/server.py"
            ]
            
            all_files_exist = True
            for file in required_files:
                if not (temp_dir_path / "plex-mcp" / file).exists():
                    print(f"❌ Missing required file: {file}")
                    all_files_exist = False
            
            if not all_files_exist:
                return False
            
            # Verify manifest
            manifest_path = temp_dir_path / "plex-mcp" / "dxt_manifest.json"
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # Check required fields
                required_fields = ["name", "version", "description", "prompts"]
                for field in required_fields:
                    if field not in manifest:
                        print(f"❌ Missing required field in manifest: {field}")
                        return False
                
                # Verify prompts
                if not isinstance(manifest["prompts"], list):
                    print("❌ 'prompts' must be a list")
                    return False
                
                # Check each prompt
                for i, prompt in enumerate(manifest["prompts"):
                    if not isinstance(prompt, dict):
                        print(f"❌ Prompt at index {i} is not an object")
                        return False
                    
                    required_prompt_fields = ["name", "description", "template"]
                    for field in required_prompt_fields:
                        if field not in prompt:
                            print(f"❌ Prompt '{prompt.get('name', f'at index {i}')}' is missing required field: {field}")
                            return False
                
                print(f"✅ Found {len(manifest['prompts'])} valid prompt templates")
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in manifest: {e}")
                return False
            
            return True
            
        except zipfile.BadZipFile:
            print(f"❌ Invalid ZIP file: {dxt_path}")
            return False
        except Exception as e:
            print(f"❌ Error verifying package: {e}")
            return False

def main() -> None:
    """Main function to verify the DXT package."""
    print("🔍 Verifying Plex MCP DXT package...")
    
    dxt_path = Path("dist/plex-mcp.dxt")
    
    if not dxt_path.exists():
        print("❌ DXT package not found. Run build_dxt.py first.")
        return
    
    if verify_dxt_package(dxt_path):
        print("\n✨ DXT package verification successful!")
        print(f"📦 Package is ready to use: {dxt_path}")
    else:
        print("\n❌ DXT package verification failed. Please check the errors above.")

if __name__ == "__main__":
    main()
